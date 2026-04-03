"""Leaderboard endpoints"""
from fastapi import APIRouter
from app.services.leaderboard_service import LeaderboardService

router = APIRouter()
lb_service = LeaderboardService()


@router.get("/")
async def get_leaderboard(limit: int = 20):
    return await lb_service.get_top(limit)


@router.get("/player/{player_id}")
async def get_player_rank(player_id: str):
    return await lb_service.get_player_rank(player_id)
