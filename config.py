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
    GIT_ACTIONS_WEBHOOK_SECRET: str = ""
    CLOUD_SCHEDULER_SECRET: str = ""
    GITHUB_TOKEN: str = ""
    GITHUB_REPO: str = "Babahan-0906/kaist-cafeteria-menu"
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding='utf-8', 
        extra="ignore"
    )

settings = Settings()
