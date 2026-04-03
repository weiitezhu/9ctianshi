"""Leaderboard service"""
from app.infra.database import get_db_connection


class LeaderboardService:
    async def get_top(self, limit: int = 20):
        db = await get_db_connection()
        try:
            cursor = await db.execute(
                "SELECT player_id, nickname, highest_level, total_score "
                "FROM players ORDER BY highest_level DESC, total_score DESC "
                "LIMIT ?",
                (limit,),
            )
            rows = await cursor.fetchall()
            return [
                {
                    "player_id": r[0],
                    "nickname": r[1],
                    "highest_level": r[2],
                    "total_score": r[3],
                }
                for r in rows
            ]
        finally:
            await db.close()

    async def get_player_rank(self, player_id: str):
        db = await get_db_connection()
        try:
            cursor = await db.execute(
                "SELECT player_id, nickname, highest_level, total_score "
                "FROM players WHERE player_id = ?",
                (player_id,),
            )
            row = await cursor.fetchone()
            if not row:
                return {"found": False}
            return {
                "found": True,
                "player_id": row[0],
                "nickname": row[1],
                "highest_level": row[2],
                "total_score": row[3],
            }
        finally:
            await db.close()
