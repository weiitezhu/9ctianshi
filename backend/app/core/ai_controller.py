"""AI controller - LLM interaction with strategy injection"""
import random
from app.infra.llm_adapter import QwenAdapter
from app.core.session_manager import GameSession
from app.prompts.base_prompt import PromptBuilder


# Model config per level range: (model, temperature, max_tokens)
MODEL_CONFIG = {
    range(1, 4): ("qwen-turbo", 0.7, 512),
    range(4, 7): ("qwen-plus", 0.5, 768),
    range(7, 10): ("qwen-plus", 0.4, 1024),
}


def _get_model_config(level_id: int):
    for rng, cfg in MODEL_CONFIG.items():
        if level_id in rng:
            return cfg
    return "qwen-plus", 0.5, 1024


class AIController:
    def __init__(self):
        self.llm = QwenAdapter()
        self.prompt_builder = PromptBuilder()

    def decide_lie(self, strategy: dict, session: GameSession) -> bool:
        prob = strategy.get("lie_probability", 0.3)
        can_consecutive = strategy.get("can_lie_consecutively", False)
        if not can_consecutive and session.messages:
            for msg in reversed(session.messages):
                if msg.get("role") == "ai" and msg.get("metadata", {}).get("was_lie"):
                    return False
        return random.random() < prob

    async def generate(self, messages: list, level_id: int) -> str:
        model, temp, max_tok = _get_model_config(level_id)
        return await self.llm.chat(
            messages=messages,
            model=model,
            temperature=temp,
            max_tokens=max_tok,
        )

    async def generate_opening(self, session: GameSession, level) -> str:
        dynamic_ctx = {
            "current_round": 0,
            "max_rounds": session.max_rounds,
            "moves_left": session.moves_left,
            "score": 0,
            "should_lie_this_round": False,
            **session.game_state,
        }
        system_prompt = self.prompt_builder.build(
            session.level_id, dynamic_ctx, session.strategy_config
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "一位挑战者来到了你的试炼之地。请说出你的开场白。"},
        ]
        return await self.generate(messages, session.level_id)

    async def generate_response(self, session: GameSession, level, user_input: str) -> str:
        """Generate AI response for normal chat (not game actions)."""
        dynamic_ctx = {
            "current_round": session.current_round,
            "max_rounds": session.max_rounds,
            "moves_left": session.moves_left,
            "score": session.score,
            "should_lie_this_round": self.decide_lie(session.strategy_config, session),
            **session.game_state,
        }
        system_prompt = self.prompt_builder.build(
            session.level_id, dynamic_ctx, session.strategy_config
        )

        # Build message history (last 10 messages)
        history = session.messages[-10:]
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            role = "user" if msg.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": msg.get("content", "")})
        messages.append({"role": "user", "content": user_input})

        response = await self.generate(messages, session.level_id)

        # Track for session history
        session.messages.append({"role": "user", "content": user_input})
        lie = dynamic_ctx["should_lie_this_round"]
        session.messages.append({"role": "ai", "content": response, "metadata": {"was_lie": lie}})

        return response
