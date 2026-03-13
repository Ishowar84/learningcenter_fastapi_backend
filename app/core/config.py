from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Learning Center API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api" # Changed from /api/v1 to /api for seamless frontend integration
    
    # Security
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_CHANGE_ME"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: Optional[str] = "sqlite:///./sql_app.db"
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
