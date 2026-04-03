"""Level 8: Mirror Duel"""
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession
from app.core.level_manager import level_manager


class Level08(BaseLevel):
    level_id = 8
    name = "Mirror Duel"
    description = "The mirror reflects everything. Unpredictability wins."
    difficulty = 0.8
    rules_hint = "7 rounds sword-shield-mirror. God reads your patterns."
    deity_name = "Mirror"
    win_rate_estimate = "~25%"

    def __init__(self):
        level_manager.register(8, self)

    async def on_start(self, session: GameSession) -> None:
        session.max_rounds = 7
        session.moves_left = 7
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
        return {"level_id": 8, "strategy": "unpredictability"}


Level08()
