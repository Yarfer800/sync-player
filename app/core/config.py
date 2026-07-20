from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    token: str
    database_url: str
    admin_id: int
    redis_url: str = "redis://localhost:6379"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

