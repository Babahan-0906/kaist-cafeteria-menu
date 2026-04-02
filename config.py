from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # api keys
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    GEMINI_API_KEY: str
    
    # configuration
    PORT: int = 8080
    HOST: str = "0.0.0.0"
    DEBUG_SCRAPER: bool = False
    GIT_ACTIONS_WEBHOOK_SECRET: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding='utf-8', 
        extra="ignore"
    )

settings = Settings()
