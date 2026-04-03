"""Game endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.game_service import GameService

router = APIRouter()
game_service = GameService()


class StartRequest(BaseModel):
    player_id: str
    level_id: int


class ActionRequest(BaseModel):
    player_id: str
    action_type: str
    content: str = ""


@router.post("/start")
async def start_game(req: StartRequest):
    result = await game_service.start_game(req.player_id, req.level_id)
    if not result:
        raise HTTPException(status_code=400, detail="Cannot start game")
    return result


@router.get("/status/{player_id}")
async def get_status(player_id: str):
    return await game_service.get_status(player_id)


@router.post("/action")
async def do_action(req: ActionRequest):
    result = await game_service.handle_action(
        req.player_id, req.action_type, req.content
    )
    if not result:
        raise HTTPException(status_code=400, detail="Invalid action")
    return result
