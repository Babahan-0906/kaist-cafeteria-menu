from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    GEMINI_API_KEY: str
    
    # Configuration
    PORT: int = 8080
    HOST: str = "0.0.0.0"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
