"""Level 3: Ultimatum"""
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession
from app.core.level_manager import level_manager


class Level03(BaseLevel):
    level_id = 3
    name = "Ultimatum"
    description = "100 coins. Your offer decides God's mood."
    difficulty = 0.4
    rules_hint = "Propose split fairly or both get nothing."
    deity_name = "Divider"
    win_rate_estimate = "~50%"

    def __init__(self):
        level_manager.register(3, self)

    async def on_start(self, session: GameSession) -> None:
        session.max_rounds = 3
        session.moves_left = 3
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
        return {"level_id": 3, "strategy": "fairness"}


Level03()
