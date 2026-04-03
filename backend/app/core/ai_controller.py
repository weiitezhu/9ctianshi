"""AI controller - LLM interaction"""
import random
from typing import Optional
from app.infra.llm_adapter import QwenAdapter
from app.core.session_manager import GameSession
from app.prompts.base_prompt import PromptBuilder


MODEL_STRATEGY = {
    1: ("qwen-turbo", 0.7, 512),
    2: ("qwen-turbo", 0.6, 768),
    3: ("qwen-plus", 0.5, 1024),
}


class AIController:
    def __init__(self):
        self.llm = QwenAdapter()
        self.prompt_builder = PromptBuilder()

    def decide_lie(self, strategy: dict, session: GameSession) -> bool:
        prob = strategy.get("lie_probability", 0.3)
        can_consecutive = strategy.get("can_lie_consecutively", False)

        if not can_consecutive and session.messages:
            for msg in reversed(session.messages):
                if msg.get("role") == "ai":
                    if msg.get("metadata", {}).get("was_lie"):
                        return False
                    break

        return random.random() < prob

    async def generate(self, messages: list, level_id: int) -> str:
        model, temp, max_tok = MODEL_STRATEGY.get(
            level_id, ("qwen-plus", 0.5, 1024)
        )
        return await self.llm.chat(
            messages=messages,
            model=model,
            temperature=temp,
            max_tokens=max_tok,
        )

    async def generate_opening(self, session, level) -> str:
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
            {
                "role": "user",
                "content": "一位挑战者来到了你的试炼之地。请说出你的开场白。",
            },
        ]
        return await self.generate(messages, session.level_id)
