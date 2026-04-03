"""Level registry - simplified"""
from typing import Dict, Optional
from app.levels.base import BaseLevel


class LevelManager:
    def __init__(self):
        self._levels: Dict[int, BaseLevel] = {}

    def register(self, level_id: int, level: BaseLevel):
        self._levels[level_id] = level

    def get_level(self, level_id: int) -> Optional[BaseLevel]:
        return self._levels.get(level_id)

    def list_levels(self):
        return [
            {"id": lid, "name": lv.name, "difficulty": lv.difficulty,
             "description": lv.description, "deity_name": lv.deity_name,
             "win_rate": lv.win_rate_estimate}
            for lid, lv in sorted(self._levels.items())
        ]

    # ── Session factory ──────────────────────────────────────
    def create_session_for_player(self, player_id: str, level_id: int):
        """Create/replace session for player at given level."""
        from app.core.session_manager import session_manager
        return session_manager.create_session(player_id, level_id, {})


level_manager = LevelManager()


def register_all_levels():
    """Import and register all 9 levels. Call once at app startup."""
    from app.levels import (
        level_01, level_02, level_03, level_04, level_05,
        level_06, level_07, level_08, level_09,
    )
