"""Level 1: Gate of Lies"""
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession
from app.core.level_manager import level_manager


class Level01(BaseLevel):
    level_id = 1
    name = "Gate of Lies"
    description = "God sets heavy fog. Only one door leads to truth."
    difficulty = 0.15
    rules_hint = "Each scene is unique. Think carefully, hints may be lies."
    deity_name = "Titing"
    win_rate_estimate = "~60%"

    def __init__(self):
        level_manager.register(1, self)

    async def on_start(self, session: GameSession) -> None:
        session.max_rounds = 5
        session.moves_left = 5
        session.score = 0.0
        session.game_state = {}

    async def on_message(
        self, session: GameSession, user_input: str
    ) -> LevelResponse:
        # All game logic is handled by GameEngine + AI
        # This stub returns a placeholder; real logic is in game_engine.py
        return LevelResponse(ai_text=None, is_action=False)

    async def judge(self, session: GameSession):
        return None

    def get_default_strategy(self) -> dict:
        return {"level_id": 1, "strategy": "deception"}


Level01()
