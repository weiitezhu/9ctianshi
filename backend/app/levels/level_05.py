"""Level 5: Trust Bridge"""
from app.levels.base import BaseLevel, LevelResponse
from app.core.session_manager import GameSession
from app.core.level_manager import level_manager


class Level05(BaseLevel):
    level_id = 5
    name = "Trust Bridge"
    description = "You on one end, God on the other. An interferer whispers lies."
    difficulty = 0.55
    rules_hint = "5 rounds. Pass 3 to cross the bridge."
    deity_name = "Keeper"
    win_rate_estimate = "~40%"

    def __init__(self):
        level_manager.register(5, self)

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
        return {"level_id": 5, "strategy": "trust"}


Level05()
