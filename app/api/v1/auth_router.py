from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas.token import LoginResponse
from app.schemas.user import User, UserUpdate, ChangePasswordRequest
from app.services import user_service

router = APIRouter()

from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login", response_model=LoginResponse)
async def login(
    request_data: LoginRequest,
    db: Session = Depends(deps.get_db)
):
    """
    JSON token login, retrieve an access token for future requests.
    """
    user = user_service.authenticate(
        db, email=request_data.email, password=request_data.password
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

@router.put("/user", response_model=User)
@router.patch("/user", response_model=User)
async def update_current_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update current user profile.
    """
    update_data = user_in.dict(exclude_unset=True)
    
    # Special handling for first_name + last_name -> name
    if "first_name" in update_data or "last_name" in update_data:
        fn = update_data.get("first_name", current_user.first_name)
        ln = update_data.get("last_name", current_user.last_name)
        update_data["name"] = f"{fn} {ln}"

    for field, value in update_data.items():
        setattr(current_user, field, value)
        
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/change-password")
async def change_password(
    *,
    db: Session = Depends(deps.get_db),
    password_in: ChangePasswordRequest,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Change password for the current user.
    """
    if not security.verify_password(password_in.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password",
        )
    
    current_user.password = security.get_password_hash(password_in.new_password)
    current_user.requires_password_reset = False # Successfully changed
    
    db.add(current_user)
    db.commit()
    return {"message": "Password updated successfully"}
