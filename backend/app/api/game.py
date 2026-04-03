"""Game API - single entry point for the new engine"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.game_engine import GameEngine

router = APIRouter()
engine = GameEngine()


class StartRequest(BaseModel):
    player_id: str
    level_id: int = 1


class ActRequest(BaseModel):
    player_id: str
    content: str


@router.post("/start")
async def start_game(req: StartRequest):
    result = await engine.start(req.player_id, req.level_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/act")
async def act(req: ActRequest):
    result = await engine.act(req.player_id, req.content)
    return result


@router.get("/status/{player_id}")
async def get_status(player_id: str):
    return await engine.get_status(player_id)


@router.get("/levels")
async def list_levels():
    from app.core.level_manager import level_manager
    return {"levels": level_manager.list_levels()}
