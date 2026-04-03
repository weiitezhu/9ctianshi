"""Nine Trials API Entry"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, game, chat, leaderboard
from app.infra.database import init_db

app = FastAPI(title="Nine Trials API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(game.router, prefix="/api/game", tags=["game"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["leaderboard"])


@app.on_event("startup")
async def startup():
    await init_db()
    from app.core.level_manager import register_all_levels
    register_all_levels()


@app.get("/health")
async def health():
    return {"status": "ok"}
