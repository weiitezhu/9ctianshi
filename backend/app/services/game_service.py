"""Game service - lifecycle management"""
from app.core.session_manager import session_manager
from app.core.level_manager import level_manager
from app.core.ai_controller import AIController


class GameService:
    def __init__(self):
        self.ai = AIController()

    async def start_game(self, player_id: str, level_id: int):
        level = level_manager.get_level(level_id)
        if not level:
            return None

        strategy = level.get_default_strategy()
        session = session_manager.create_session(player_id, level_id, strategy)

        opening = await self.ai.generate_opening(session, level)
        return {
            "session_id": session.session_id,
            "level_id": level_id,
            "level_name": level.name,
            "opening_message": opening,
            "rules_hint": level.rules_hint,
        }

    async def get_status(self, player_id: str):
        session = session_manager.get_active_session(player_id)
        if not session:
            return {"status": "no_active_session"}
        return {
            "status": session.status.value,
            "level_id": session.level_id,
            "current_round": session.current_round,
            "score": session.score,
            "moves_left": session.moves_left,
        }

    async def handle_action(self, player_id: str, action_type: str, content: str):
        session = session_manager.get_active_session(player_id)
        if not session:
            return None

        level = level_manager.get_level(session.level_id)
        result = await level.handle_action(session, action_type, content)
        return result

    async def get_result(self, player_id: str, level_id: int):
        session = session_manager.get_session(player_id, level_id)
        if not session:
            return {"status": "not_found"}
        return {
            "status": session.status.value,
            "score": session.score,
            "rounds": session.current_round,
        }
