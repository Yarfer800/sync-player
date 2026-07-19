from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    token: str
    database_url: str
    system_prompt: str
    admin_id: int
    ai_api_key: str
    text_model: str
    text_model_api_key: str
    image_model: str
    image_model_api_key: str
    redis_url: str = "redis://localhost:6379"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

