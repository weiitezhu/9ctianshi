"""Qwen LLM adapter via DashScope OpenAI-compatible API"""
import httpx
import json
from app.config import settings


class QwenAdapter:
    def __init__(self):
        self.base_url = settings.QWEN_BASE_URL
        self.api_key = settings.QWEN_API_KEY

    async def chat(
        self,
        messages: list,
        model: str = "qwen-plus",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
