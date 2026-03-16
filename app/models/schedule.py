import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from app.db.session import Base

class ScheduleRecurrence(Base):
    __tablename__ = "schedule_recurrences"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(String, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    location = Column(Text)
    
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    
    frequency = Column(String, nullable=False)
    interval = Column(Integer, nullable=False, default=1)
    weekdays = Column(Text)
    month_day = Column(Integer)
    
    end_type = Column(String, nullable=False, default="never")
    end_date = Column(DateTime(timezone=True))
    occurrence_count = Column(Integer)
    
    timezone = Column(String, default="UTC")
    notes = Column(Text)
    external_link = Column(Text)
    created_by = Column(String, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(String, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    regular_teacher_id = Column(String, ForeignKey("users.id", ondelete="RESTRICT"))
    student_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    
    title = Column(String, nullable=False)
    description = Column(Text)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    location = Column(Text)
    external_link = Column(Text)
    status = Column(String, nullable=False, default="scheduled")
    notes = Column(Text)
    
    recurrence_id = Column(String, ForeignKey("schedule_recurrences.id", ondelete="CASCADE"))
    occurrence_index = Column(Integer)
    original_start_time = Column(DateTime(timezone=True))
    is_exception = Column(Boolean, default=False)
    
    created_by = Column(String, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    cancelled_by = Column(String, ForeignKey("users.id", ondelete="RESTRICT"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
