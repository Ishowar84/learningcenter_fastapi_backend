from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas.token import LoginResponse
from app.schemas.user import User
from app.services import user_service

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, retrieve an access token for future requests.
    """
    user = user_service.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active. Please wait for parent authorization.",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    # In a real app, generate a proper refresh token stored in DB
    # For now, we'll return a placeholder or another JWT
    refresh_token = security.create_access_token(
        subject=user.id, expires_delta=timedelta(days=7)
    )
    
    return {
        "success": True,
        "user": user,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "requires_password_reset": user.requires_password_reset
    }

@router.get("/user", response_model=User)
async def read_current_user_info(
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get current logged in user information.
    """
    return current_user
