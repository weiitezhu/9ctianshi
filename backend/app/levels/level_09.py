"""Level 9: God's Trial"""
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession
from app.core.level_manager import level_manager


class Level09(BaseLevel):
    level_id = 9
    name = "God's Trial"
    description = "Final trial. Three phases await."
    difficulty = 0.92
    rules_hint = "Three consecutive challenges: truth, sacrifice, judgment."
    deity_name = "God"
    win_rate_estimate = "~15%"

    def __init__(self):
        level_manager.register(9, self)

    async def on_start(self, session: GameSession) -> None:
        session.max_rounds = 9
        session.moves_left = 9
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
        return {"level_id": 9, "strategy": "final_boss"}


Level09()
