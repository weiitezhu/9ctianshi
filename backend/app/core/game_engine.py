"""Game Engine - scene generation, judgment, auto-progression"""
from app.core.session_manager import session_manager, SessionStatus
from app.core.level_manager import level_manager
from app.core.ai_controller import AIController


class GameEngine:
    def __init__(self):
        self.ai = AIController()

    async def start(self, player_id: str, level_id: int = 1) -> dict:
        level = level_manager.get_level(level_id)
        if not level:
            return {"error": f"Level {level_id} not found"}
        session = session_manager.create_session(player_id, level_id, {})
        await level.on_start(session)
        scene = await self.ai.generate_scene(session, level)
        session.game_state["current_scene"] = scene
        session.game_state["options"] = scene.get("options", [])
        return {
            "session_id": session.session_id,
            "level_id": level_id,
            "level_name": level.name,
            "level_intro": scene.get("intro", ""),
            "scene_text": scene.get("text", ""),
            "options": scene.get("options", []),
            "hint": scene.get("hint", ""),
            "win_condition": scene.get("win_condition", ""),
            "rounds_left": session.moves_left,
            "score": 0.0,
        }

    async def act(self, player_id: str, player_input: str) -> dict:
        session = session_manager.get_active_session(player_id)
        if not session:
            return {"type": "error", "content": "No active game. Start one first."}
        if session.status == SessionStatus.COMPLETED:
            return {
                "type": "game_over",
                "content": "This game is over. Start a new one.",
                "result": session.game_state.get("_last_result"),
                "score": session.score,
            }
        level = level_manager.get_level(session.level_id)
        current_scene = session.game_state.get("current_scene", {})
        result = await self.ai.judge_input(
            session=session,
            level=level,
            player_input=player_input,
            current_scene=current_scene,
        )
        result_type = result.get("type", "continue")
        score_delta = result.get("score_delta", 0)
        session.score += score_delta
        session.current_round += 1
        session.moves_left = max(0, session.moves_left - 1)
        if result_type == "win":
            session.game_state["_last_result"] = "won"
            session.status = SessionStatus.COMPLETED
            session.score = 100.0
            win_text = result.get("text", "你赢了！")
            next_id = session.level_id + 1
            has_next = level_manager.get_level(next_id) is not None
            return {
                "type": "game_over",
                "result": "won",
                "score": 100.0,
                "ai_text": win_text,
                "level_complete": True,
                "next_level_id": next_id if has_next else None,
                "has_next": has_next,
                "total_score": session.score,
            }
        if result_type == "lose":
            session.game_state["_last_result"] = "lost"
            session.status = SessionStatus.COMPLETED
            lose_text = result.get("text", "你输了。")
            return {
                "type": "game_over",
                "result": "lost",
                "score": session.score,
                "ai_text": lose_text,
                "level_complete": False,
                "retry_level_id": session.level_id,
                "has_next": level_manager.get_level(session.level_id) is not None,
                "total_score": session.score,
            }
        next_scene = await self.ai.generate_scene(session, level, player_input)
        session.game_state["current_scene"] = next_scene
        session.game_state["options"] = next_scene.get("options", [])
        return {
            "type": "continue",
            "ai_text": result.get("text", ""),
            "scene_text": next_scene.get("text", ""),
            "options": next_scene.get("options", []),
            "hint": next_scene.get("hint", ""),
            "win_condition": next_scene.get("win_condition", ""),
            "rounds_left": session.moves_left,
            "score": session.score,
        }

    async def get_status(self, player_id: str) -> dict:
        session = session_manager.get_active_session(player_id)
        if not session:
            return {"status": "no_session"}
        lv = level_manager.get_level(session.level_id)
        return {
            "status": session.status.value,
            "level_id": session.level_id,
            "level_name": lv.name if lv else "?",
            "rounds_left": session.moves_left,
            "score": session.score,
        }
