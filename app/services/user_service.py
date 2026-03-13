import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    db_obj = User(
        id=str(uuid.uuid4()),
        email=user_in.email,
        password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        name=f"{user_in.first_name} {user_in.last_name}" if user_in.first_name and user_in.last_name else user_in.name,
        role=user_in.role,
        is_active=user_in.is_active,
        phone=user_in.phone,
        address=user_in.address,
        city=user_in.city,
        state=user_in.state,
        zip_code=user_in.zip_code,
        country=user_in.country,
        bio=user_in.bio,
        date_of_birth=user_in.date_of_birth,
        gender=user_in.gender,
        subject=user_in.subject,
        education=user_in.education,
        certifications=user_in.certifications,
        parent_id=user_in.parent_id,
        avatar_url=user_in.avatar_url,
        profile_image_url=user_in.profile_image_url,
        cover_photo_url=user_in.cover_photo_url,
        calendar_color=user_in.calendar_color,
        timezone=user_in.timezone,
        partner_id=user_in.partner_id,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def authenticate(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not user.password: # Should not happen with new users but for safety
        return None
    if not verify_password(password, user.password):
        return None
    return user
