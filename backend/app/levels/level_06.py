"""Level 6: Pirate's Gold"""
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession
from app.core.level_manager import level_manager


class Level06(BaseLevel):
    level_id = 6
    name = "Pirate's Gold"
    description = "You're pirate #2. Propose a split, the crew votes."
    difficulty = 0.65
    rules_hint = "Split 100 gems. Majority vote or overboard."
    deity_name = "Divider"
    win_rate_estimate = "~35%"

    def __init__(self):
        level_manager.register(6, self)

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
        return {"level_id": 6, "strategy": "strategy"}


Level06()
