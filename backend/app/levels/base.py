"""Base level - abstract interface"""
from abc import ABC, abstractmethod
from app.core.session_manager import GameSession


class BaseLevel(ABC):
    level_id: int = 0
    name: str = ""
    difficulty: float = 0.0
    rules_hint: str = ""

    @abstractmethod
    async def start(self, session: GameSession) -> dict:
        """Initialize level state"""
        ...

    @abstractmethod
    async def preprocess(self, session: GameSession, user_input: str) -> dict | None:
        """Check if input is a game action. Return None for normal chat."""
        ...

    @abstractmethod
    async def handle_action(
        self, session: GameSession, action_type: str, content: str
    ) -> dict:
        """Handle game action (select door, etc.)"""
        ...

    @abstractmethod
    async def check_round_end(self, session: GameSession) -> dict | None:
        """Check if round ends, return event or None"""
        ...

    @abstractmethod
    async def judge(self, session: GameSession) -> dict | None:
        """Judge win/lose. Return result or None if not ended."""
        ...

    @abstractmethod
    def get_default_strategy(self) -> dict:
        """Return default strategy config for this level"""
        ...
