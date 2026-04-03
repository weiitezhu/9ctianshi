"""Chat service - orchestrates AI conversation"""
from app.core.session_manager import session_manager
from app.core.level_manager import level_manager
from app.core.ai_controller import AIController
from app.prompts.base_prompt import PromptBuilder
from app.core.judge import Judge


class ChatService:
    def __init__(self):
        self.ai = AIController()
        self.judge = Judge()
        self.prompt_builder = PromptBuilder()

    async def handle_message(self, player_id: str, content: str):
        if not player_id:
            return {"type": "error", "content": "Not initialized"}

        session = session_manager.get_active_session(player_id)
        if not session:
            return {"type": "error", "content": "No active session"}

        import time as _time
        session.updated_at = _time.time()
        session.messages.append({"role": "player", "content": content})

        level = level_manager.get_level(session.level_id)

        # Let level preprocess
        preprocess = await level.preprocess(session, content)
        if preprocess and preprocess.get("is_game_action"):
            action_result = await level.handle_action(
                session, preprocess["action_type"], content
            )
            return action_result

        # Decide lie
        should_lie = self.ai.decide_lie(session.strategy_config, session)

        # Build prompt
        dynamic_ctx = {
            "current_round": session.current_round,
            "max_rounds": session.max_rounds,
            "moves_left": session.moves_left,
            "score": session.score,
            "should_lie_this_round": should_lie,
            **session.game_state,
        }
        system_prompt = self.prompt_builder.build(
            session.level_id, dynamic_ctx, session.strategy_config
        )

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        for msg in session.messages[-10:]:
            role = "assistant" if msg["role"] == "ai" else "user"
            messages.append({"role": role, "content": msg["content"]})

        # Call LLM
        ai_response = await self.ai.generate(messages, session.level_id)

        session.messages.append({
            "role": "ai",
            "content": ai_response,
            "metadata": {"was_lie": should_lie},
        })

        session.current_round += 1

        # Check round end
        events = []
        round_result = await level.check_round_end(session)
        if round_result:
            events.append(round_result)

        game_over = await level.judge(session)
        if game_over:
            from app.core.session_manager import SessionStatus
            session.status = SessionStatus.COMPLETED
            events.append(game_over)

        response = {
            "type": "ai_message",
            "content": ai_response,
        }
        if events:
            response["events"] = events

        return response
