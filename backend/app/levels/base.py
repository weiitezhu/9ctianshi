"""Base level interface"""
from abc import ABC, abstractmethod
from app.core.session_manager import GameSession

class BaseLevel(ABC):
    level_id: int = 0
    name: str = ""
    description: str = ""
    difficulty: float = 0.0
    rules_hint: str = ""
    deity_name: str = ""
    win_rate_estimate: str = ""

    @abstractmethod
    async def on_start(self, session: GameSession) -> None: ...
    @abstractmethod
    async def on_message(self, session: GameSession, user_input: str) -> "LevelResponse": ...
    @abstractmethod
    async def judge(self, session: GameSession) -> dict | None: ...
    @abstractmethod
    def get_default_strategy(self) -> dict: ...

    def get_level_info(self):
        return {"id": self.level_id, "name": self.name, "description": self.description,
                "difficulty": self.difficulty, "rules_hint": self.rules_hint,
                "deity_name": self.deity_name, "win_rate": self.win_rate_estimate}

class LevelResponse:
    def __init__(self, ai_text=None, game_event=None, is_action=False, end_turn=True):
        self.ai_text = ai_text; self.game_event = game_event
        self.is_action = is_action; self.end_turn = end_turn
    def to_dict(self):
        return {k: v for k, v in {"ai_text": self.ai_text, "game_event": self.game_event,
                "is_action": self.is_action, "end_turn": self.end_turn}.items() if v is not None}
