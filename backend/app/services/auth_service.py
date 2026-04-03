"""Auth service - WeChat login"""
import httpx
from app.config import settings


class AuthService:
    async def login(self, code: str):
        """WeChat code2session"""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.weixin.qq.com/sns/jscode2session",
                    params={
                        "appid": settings.WECHAT_APP_ID,
                        "secret": settings.WECHAT_APP_SECRET,
                        "js_code": code,
                        "grant_type": "authorization_code",
                    },
                )
                data = resp.json()
                openid = data.get("openid")
                if not openid:
                    return None
                return {
                    "player_id": openid,
                    "token": openid,  # MVP: use openid as token
                    "nickname": f"player_{openid[:6]}",
                }
        except Exception:
            return None
