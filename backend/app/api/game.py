"""Game endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.game_service import GameService

router = APIRouter()
game_service = GameService()


class StartRequest(BaseModel):
    player_id: str
    level_id: int


class MessageRequest(BaseModel):
    player_id: str
    content: str


@router.post("/start")
async def start_game(req: StartRequest):
    result = await game_service.start_game(req.player_id, req.level_id)
    if not result:
        raise HTTPException(status_code=400, detail="Cannot start game")
    return result


@router.get("/status/{player_id}")
async def get_status(player_id: str):
    return await game_service.get_status(player_id)


@router.post("/message")
async def send_message(req: MessageRequest):
    """Send a text message and get AI + game response."""
    result = await game_service.handle_message(req.player_id, req.content)
    return result


@router.get("/levels")
async def list_levels():
    from app.core.level_manager import level_manager
    return {"levels": level_manager.list_levels()}


@router.post("/action")
async def do_action(req: MessageRequest):
    result = await game_service.handle_message(req.player_id, req.content)
    return result
