from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    rp_user_id: str = ""
    min_rating: int = 6
    anthropic_api_key: str = ""
    ai_model: str = "claude-opus-5-5"
    notify_min_score: int = 7
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
