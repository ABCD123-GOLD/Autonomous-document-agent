from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # API Security
    API_KEY: str = "dev_key"
    
    # LLM Providers
    OPENAI_API_KEY: str
    
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    # App Settings
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
