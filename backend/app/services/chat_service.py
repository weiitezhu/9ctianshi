"""Chat service - orchestrates AI conversation + level logic"""
from app.core.session_manager import session_manager, SessionStatus
from app.core.level_manager import level_manager
from app.core.ai_controller import AIController


class ChatService:
    def __init__(self):
        self.ai = AIController()

    async def handle_message(self, player_id: str, content: str) -> dict:
        if not player_id:
            return {"type": "error", "content": "Not initialized"}

        session = session_manager.get_active_session(player_id)
        if not session:
            return {"type": "error", "content": "No active session. Start a game first."}

        if session.status == SessionStatus.COMPLETED:
            return {
                "type": "game_over",
                "content": "This game is over. Start a new one with /start.",
            }

        level = level_manager.get_level(session.level_id)
        if not level:
            return {"type": "error", "content": "Level not found."}

        # Process through level
        response = await level.on_message(session, content)

        # Update session
        if response.end_turn:
            session.current_round += 1
        session.messages.append({"role": "player", "content": content})
        session.updated_at = session.messages[-1].get("__time", session.updated_at)

        # Game action → return directly
        if response.is_action:
            session.status = SessionStatus.COMPLETED
            return response.game_event or {}

        # Normal chat → generate AI response
        ai_text = await self.ai.generate_response(session, level, content)

        # Check if level ended
        game_over = await level.judge(session)
        if game_over:
            session.status = SessionStatus.COMPLETED
            return {
                "ai_text": ai_text,
                "game_event": game_over,
                "events": [game_over],
            }

        return {
            "ai_text": ai_text,
            "game_event": response.game_event,
        }
