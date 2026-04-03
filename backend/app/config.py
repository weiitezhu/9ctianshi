"""Global settings"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""
    SESSION_TIMEOUT: int = 1800
    DEFAULT_MODEL: str = "qwen-plus"

    class Config:
        env_file = ".env"


settings = Settings()
