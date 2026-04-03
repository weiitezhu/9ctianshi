"""Multi-session manager"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional
import uuid
import time


class SessionStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"


@dataclass
class GameSession:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str = ""
    level_id: int = 1
    status: SessionStatus = SessionStatus.ACTIVE

    current_round: int = 0
    max_rounds: int = 10
    score: float = 0.0
    moves_left: int = 3
    game_state: dict = field(default_factory=dict)

    strategy_config: dict = field(default_factory=dict)
    messages: list = field(default_factory=list)

    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    expires_at: float = 0.0

    def __post_init__(self):
        if self.expires_at == 0.0:
            self.expires_at = self.created_at + 1800


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, Dict[int, GameSession]] = {}

    def create_session(
        self, player_id: str, level_id: int, strategy_config: dict
    ) -> GameSession:
        if player_id not in self._sessions:
            self._sessions[player_id] = {}

        player_sessions = self._sessions[player_id]

        if level_id in player_sessions:
            old = player_sessions[level_id]
            if old.status == SessionStatus.ACTIVE:
                old.status = SessionStatus.PAUSED

        session = GameSession(
            player_id=player_id,
            level_id=level_id,
            strategy_config=strategy_config,
        )
        player_sessions[level_id] = session
        return session

    def get_session(
        self, player_id: str, level_id: int
    ) -> Optional[GameSession]:
        sessions = self._sessions.get(player_id, {})
        session = sessions.get(level_id)
        if session and session.status == SessionStatus.EXPIRED:
            return None
        return session

    def get_active_session(
        self, player_id: str
    ) -> Optional[GameSession]:
        sessions = self._sessions.get(player_id, {})
        for session in sessions.values():
            if session.status == SessionStatus.ACTIVE:
                return session
        return None

    def cleanup_expired(self):
        now = time.time()
        for player_sessions in self._sessions.values():
            for session in player_sessions.values():
                if (
                    session.status == SessionStatus.ACTIVE
                    and session.expires_at < now
                ):
                    session.status = SessionStatus.EXPIRED


session_manager = SessionManager()
