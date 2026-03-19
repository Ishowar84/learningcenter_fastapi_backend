import uuid
from sqlalchemy import Column, String, Text, ForeignKey, Date, Boolean, DateTime, JSON

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    grade = Column(String) # Grade/class level for the subject
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Course(Base):
    __tablename__ = "courses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True, nullable=False)
    description = Column(Text)
    teacher_id = Column(String, ForeignKey("users.id", ondelete="RESTRICT"))
    subject = Column(String, nullable=False) # In the Node schema, this is text
    grade = Column(String, nullable=False)
    start_date = Column(Date)
    duration = Column(String) # e.g., "12 weeks"
    philosophy = Column(Text)
    prerequisites = Column(Text)
    learning_objectives = Column(Text)
    curriculum = Column(JSON) # Generic JSON works on both SQLite and PostgreSQL
    practical_sessions = Column(Text)
    cover_image_url = Column(String)
    is_active = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

