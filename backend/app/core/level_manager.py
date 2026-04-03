"""Level registry"""
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
        return [{"id": lid, "name": lv.name, "difficulty": lv.difficulty}
                for lid, lv in sorted(self._levels.items())]


level_manager = LevelManager()


def register_all_levels():
    """Import and register all levels. Call this at app startup."""
    from app.levels import level_01, level_02, level_03, level_04, level_05
    from app.levels import level_06, level_07, level_08, level_09
