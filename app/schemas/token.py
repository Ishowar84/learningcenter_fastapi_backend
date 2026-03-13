from typing import Optional
from app.schemas.base import CamelModel
from app.schemas.user import User

class Token(CamelModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"

class LoginResponse(CamelModel):
    success: bool
    user: User
    access_token: str
    refresh_token: Optional[str] = None
    requires_password_reset: Optional[bool] = None
