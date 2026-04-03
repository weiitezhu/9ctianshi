"""Level registry and factory"""
from typing import Dict, Optional, Type
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
            {"id": lid, "name": lv.name, "difficulty": lv.difficulty}
            for lid, lv in self._levels.items()
        ]


level_manager = LevelManager()

# Auto-import and register levels
from app.levels import level_01  # noqa: E402,F401
