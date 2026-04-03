"""Auth endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()


class LoginRequest(BaseModel):
    code: str


class LoginResponse(BaseModel):
    player_id: str
    token: str
    nickname: str


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    result = await auth_service.login(req.code)
    if not result:
        raise HTTPException(status_code=401, detail="Login failed")
    return result
