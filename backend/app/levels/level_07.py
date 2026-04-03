"""Level 7: Lie Hunter"""
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession
from app.core.level_manager import level_manager


class Level07(BaseLevel):
    level_id = 7
    name = "Lie Hunter"
    description = "8 statements, 3 are lies. Separating truth from lies."
    difficulty = 0.72
    rules_hint = "Find all fake statements. God adapts to your logic."
    deity_name = "Truthseeker"
    win_rate_estimate = "~30%"

    def __init__(self):
        level_manager.register(7, self)

    async def on_start(self, session: GameSession) -> None:
        session.max_rounds = 8
        session.moves_left = 8
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
        return {"level_id": 7, "strategy": "deduction"}


Level07()
