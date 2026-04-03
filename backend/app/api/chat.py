"""WebSocket chat endpoint"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.chat_service import ChatService
import json

router = APIRouter()
chat_service = ChatService()


@router.websocket("/ws")
async def websocket_chat(ws: WebSocket):
    await ws.accept()
    player_id = None
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "init":
                player_id = msg.get("player_id")
                await ws.send_json({"type": "connected"})

            elif msg.get("type") == "message":
                content = msg.get("content", "")
                response = await chat_service.handle_message(player_id, content)
                await ws.send_json(response)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "content": str(e)})
        except Exception:
            pass
