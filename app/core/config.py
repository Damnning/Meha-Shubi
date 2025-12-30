from typing import Optional
import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    BASE_URL: str = os.getenv("BASE_URL")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = os.getenv("DB_HOST")
    DB_NAME: str = os.getenv("DB_NAME")

    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY: str = os.getenv("S3_ACCESS_KEY")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME")
    S3_ENDPOINT_URL: str = os.getenv("S3_BUCKET_NAME")
    S3_REGION: str = os.getenv("S3_REGION")

    OPENROUTER_KEY: str = os.getenv("OPENAI_KEY")
    LLM_MODEL: str = os.getenv("LLM_MODEL")

    VK_CLIENT_ID: Optional[str] = os.getenv("VK_CLIENT_ID")
    VK_CLIENT_SECRET: Optional[str] = os.getenv("VK_CLIENT_ID")
    YANDEX_CLIENT_ID: Optional[str] = os.getenv("VK_CLIENT_ID")
    YANDEX_CLIENT_SECRET: Optional[str] = os.getenv("VK_CLIENT_ID")

    TG_BOT_TOKEN: Optional[str] = None

    SESSION_SECRET: str = secrets.token_urlsafe(15)

    @property
    def DATABASE_URL(self) -> str:
        # Используем асинхронный драйвер asyncpg
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()