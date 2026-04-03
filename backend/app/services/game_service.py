"""Game service - lifecycle management"""
from app.core.session_manager import session_manager, SessionStatus
from app.core.level_manager import level_manager
from app.core.ai_controller import AIController


class GameService:
    def __init__(self):
        self.ai = AIController()

    async def start_game(self, player_id: str, level_id: int):
        level = level_manager.get_level(level_id)
        if not level:
            return None

        strategy = level.get_default_strategy()
        session = session_manager.create_session(player_id, level_id, strategy)
        await level.on_start(session)

        opening = await self.ai.generate_opening(session, level)
        return {
            "session_id": session.session_id,
            "level_id": level_id,
            "level_name": level.name,
            "level_info": level.get_level_info(),
            "opening_message": opening,
            "rules_hint": level.rules_hint,
        }

    async def get_status(self, player_id: str):
        session = session_manager.get_active_session(player_id)
        if not session:
            return {"status": "no_active_session"}
        level = level_manager.get_level(session.level_id)
        return {
            "status": session.status.value,
            "level_id": session.level_id,
            "level_name": level.name if level else "Unknown",
            "current_round": session.current_round,
            "score": session.score,
            "moves_left": session.moves_left,
            "max_rounds": session.max_rounds,
        }

    async def handle_message(self, player_id: str, content: str) -> dict:
        """Main entry: process player message through level logic + AI."""
        session = session_manager.get_active_session(player_id)
        if not session:
            return {"type": "error", "content": "No active session. Start a game first."}

        if session.status == SessionStatus.COMPLETED:
            return {"type": "game_over", "content": "This game is already over. Start a new one."}

        level = level_manager.get_level(session.level_id)
        if not level:
            return {"type": "error", "content": "Level not found."}

        # Ask level to process message
        response = await level.on_message(session, content)

        # Update session state
        session.current_round += 1
        session.updated_at = session.created_at  # refresh

        # If it's a game action (no AI call needed), return directly
        if response.is_action:
            result = response.game_event or {}
            result["ai_text"] = response.ai_text
            return result

        # Otherwise, generate AI response
        ai_text = await self.ai.generate_response(session, level, content)
        return {
            "ai_text": ai_text,
            "game_event": response.game_event,
        }

    async def get_result(self, player_id: str, level_id: int):
        session = session_manager.get_session(player_id, level_id)
        if not session:
            return {"status": "not_found"}
        return {
            "status": session.status.value,
            "score": session.score,
            "rounds": session.current_round,
        }
