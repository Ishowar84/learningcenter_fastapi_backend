import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(String, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    approval_status = Column(String, default="pending", nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    
    student = relationship("User", foreign_keys=[student_id])
    course = relationship("Course", foreign_keys=[course_id])

    __table_args__ = (
        UniqueConstraint('student_id', 'course_id', name='unique_student_course_enrollment'),
    )

class EnrollmentRequest(Base):
    __tablename__ = "enrollment_requests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(String, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(String, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    status = Column(String, default="requested", nullable=False)
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    parent_approved_at = Column(DateTime(timezone=True), nullable=True)
    admin_approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    student = relationship("User", foreign_keys=[student_id])
    course = relationship("Course", foreign_keys=[course_id])
    parent = relationship("User", foreign_keys=[parent_id])

    __table_args__ = (
        UniqueConstraint('student_id', 'course_id', name='unique_student_course_request'),
    )
