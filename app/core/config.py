from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List, Union
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Learning Center API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api" # Changed from /api/v1 to /api for seamless frontend integration
    
    # Security
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_CHANGE_ME"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    # Can be a JSON array string: ["http://localhost:5173", "http://localhost:3000"]
    # OR a comma-separated string: http://localhost:5173,http://localhost:3000
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:8081"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v
    
    # Database
    DATABASE_URL: Optional[str] = "sqlite:///./sql_app.db"
    
    # Cloud Storage (Supabase S3 Compatible)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1" # Supabase often uses us-east-1 for its S3 gateway
    S3_ENDPOINT_URL: Optional[str] = None
    S3_BUCKET_NAME: str = "assignments"
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
