from typing import Optional
from datetime import date, datetime
from pydantic import EmailStr
from app.models.user_role import UserRole
from app.schemas.base import CamelModel

class UserBase(CamelModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    role: UserRole
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    subject: Optional[str] = None
    education: Optional[str] = None
    certifications: Optional[str] = None
    parent_id: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_image_url: Optional[str] = None
    cover_photo_url: Optional[str] = None
    calendar_color: Optional[str] = None
    timezone: Optional[str] = "UTC"
    is_active: bool = True
    partner_id: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    role: Optional[UserRole] = None
    password: Optional[str] = None

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserInDB(User):
    password: Optional[str] = None
