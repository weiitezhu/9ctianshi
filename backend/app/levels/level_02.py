"""Level 2: Prisoner's Dilemma"""
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession
from app.core.level_manager import level_manager


class Level02(BaseLevel):
    level_id = 2
    name = "Prisoner's Dilemma"
    description = "You and God choose: cooperate or betray."
    difficulty = 0.3
    rules_hint = "5 rounds. God learns your strategy and adapts."
    deity_name = "Adjudicator"
    win_rate_estimate = "~50%"

    def __init__(self):
        level_manager.register(2, self)

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
        return {"level_id": 2, "strategy": "tit_for_tat"}


Level02()
