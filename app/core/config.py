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
    def assemble_cors_origins(cls, v: Union[str, List[str]], info) -> Union[List[str], str]:
        # Handle Render's ALLOWED_ORIGINS if provided
        if not v and "ALLOWED_ORIGINS" in info.data:
            v = info.data["ALLOWED_ORIGINS"]
            
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v
    
    # Render fallback for CORS
    ALLOWED_ORIGINS: Optional[str] = None
    
    # Database
    DATABASE_URL: Optional[str] = "sqlite:///./sql_app.db"
    
    # Cloud Storage (Supabase S3 Compatible)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # Render Aliases for Storage
    AWS_S3_REGION_NAME: Optional[str] = None
    AWS_S3_ENDPOINT_URL: Optional[str] = None
    AWS_STORAGE_BUCKET_NAME: Optional[str] = None
    
    # Original Storage Names with Fallbacks
    AWS_REGION: str = "us-east-1"
    S3_ENDPOINT_URL: Optional[str] = None
    S3_BUCKET_NAME: str = "assignments"

    @field_validator("DATABASE_URL", mode="before")
    def fix_postgres_url(cls, v: Optional[str]) -> Optional[str]:
        if v and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    @field_validator("AWS_REGION", mode="before")
    def set_region(cls, v: str, info) -> str:
        return info.data.get("AWS_S3_REGION_NAME") or v

    @field_validator("S3_ENDPOINT_URL", mode="before")
    def set_endpoint(cls, v: Optional[str], info) -> Optional[str]:
        return info.data.get("AWS_S3_ENDPOINT_URL") or v

    @field_validator("S3_BUCKET_NAME", mode="before")
    def set_bucket(cls, v: str, info) -> str:
        return info.data.get("AWS_STORAGE_BUCKET_NAME") or v
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
