from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date

from app.api import deps
from app.models.user_role import UserRole
from app.schemas.user import User, UserCreate, UserUpdate
from app.services import user_service
from app.models.user import User as UserModel

router = APIRouter()

@router.get("/", response_model=List[User])
async def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    current_user: UserModel = Depends(deps.get_current_user),
):
    """
    Retrieve users. Admin only filter by role or list all.
    """
    # For now, let's allow all authenticated users to list users (maybe needed for searching)
    # But usually this should be Admin only.
    query = db.query(UserModel)
    if role:
        query = query.filter(UserModel.role == role)
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=User)
async def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: UserModel = Depends(deps.get_current_user),
):
    """
    Create new user. Admin only.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    return user_service.create_user(db, user_in=user_in)

@router.get("/birthdays/today", response_model=dict)
async def get_birthdays_today(
    db: Session = Depends(deps.get_db),
):
    """
    Get users with birthdays today.
    """
    today = date.today()
    # SQLite doesn't have easy date parts, so we filter in Python for now or use strftime
    # For robust production, use database specific functions.
    users = db.query(UserModel).filter(UserModel.is_active == True).all()
    birthday_ids = [
        u.id for u in users 
        if u.date_of_birth and u.date_of_birth.month == today.month and u.date_of_birth.day == today.day
    ]
    return {"birthdayUserIds": birthday_ids, "date": today.isoformat()}

@router.get("/{user_id}", response_model=User)
async def read_user_by_id(
    user_id: str,
    current_user: UserModel = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Get a specific user by id.
    """
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return user

@router.put("/{user_id}", response_model=User)
@router.patch("/{user_id}", response_model=User)
async def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str,
    user_in: UserUpdate,
    current_user: UserModel = Depends(deps.get_current_user),
):
    """
    Update a user. Admin or the user themselves.
    """
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = user_in.dict(exclude_unset=True)
    
    # Special handling for names
    if "first_name" in update_data or "last_name" in update_data:
        fn = update_data.get("first_name", user.first_name)
        ln = update_data.get("last_name", user.last_name)
        update_data["name"] = f"{fn} {ln}"

    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str,
    current_user: UserModel = Depends(deps.get_current_user),
):
    """
    Delete a user. Admin only.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully", "id": user_id}

# Placeholder for activity logs and documents since models aren't yet defined
@router.get("/{user_id}/activity-logs", response_model=List)
async def get_user_activity_logs(user_id: str):
    return []

@router.get("/{user_id}/documents", response_model=List)
async def get_user_documents(user_id: str):
    return []

@router.get("/{user_id}/parents", response_model=Optional[User])
async def get_user_parents(user_id: str, db: Session = Depends(deps.get_db)):
    user = user_service.get_user(db, user_id)
    if user and user.parent_id:
        return user_service.get_user(db, user.parent_id)
    return None
