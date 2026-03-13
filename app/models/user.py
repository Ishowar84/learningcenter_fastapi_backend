import uuid
from sqlalchemy import Column, String, Enum as SQLEnum, Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.session import Base
from app.models.user_role import UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String) # Computed from first_name + last_name
    first_name = Column(String)
    last_name = Column(String)
    role = Column(SQLEnum(UserRole), nullable=False)
    phone = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    country = Column(String)
    bio = Column(Text)
    date_of_birth = Column(Date)
    gender = Column(String)
    subject = Column(String) # For teachers
    education = Column(String) # For teachers
    certifications = Column(String) # For teachers
    
    parent_id = Column(String, ForeignKey("users.id"), nullable=True)
    avatar_url = Column(String)
    profile_image_url = Column(String)
    cover_photo_url = Column(String)
    calendar_color = Column(String)
    timezone = Column(String, default="UTC")
    is_active = Column(Boolean, default=True)
    
    one_time_password = Column(String)
    requires_password_reset = Column(Boolean, default=False)
    reset_token = Column(String)
    reset_token_expiry = Column(DateTime)
    
    partner_id = Column(String, ForeignKey("partners.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Partner(Base):
    __tablename__ = "partners"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    status = Column(String, default="active", nullable=False) # "active", "inactive"
    state = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    address = Column(String)
    city = Column(String)
    country = Column(String)
    description = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
