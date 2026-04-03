"""Level 4: Negotiation"""
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession
from app.core.level_manager import level_manager


class Level04(BaseLevel):
    level_id = 4
    name = "Negotiation"
    description = "Three-way contract. Truth and deception coexist."
    difficulty = 0.5
    rules_hint = "3 issues, 5 rounds. Win at least 2 terms."
    deity_name = "Contract"
    win_rate_estimate = "~45%"

    def __init__(self):
        level_manager.register(4, self)

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
        return {"level_id": 4, "strategy": "bargaining"}


Level04()
