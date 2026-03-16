import uuid
from sqlalchemy import Column, String, Date, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(String, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    notes = Column(Text)
    recorded_by = Column(String, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    __table_args__ = (
        UniqueConstraint('student_id', 'course_id', 'date', name='unique_student_course_date_attendance'),
    )

    student = relationship("User", foreign_keys=[student_id])
    course = relationship("Course", foreign_keys=[course_id])
    recorder = relationship("User", foreign_keys=[recorded_by])
