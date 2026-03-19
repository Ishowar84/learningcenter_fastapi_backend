import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum

class AssignmentType(str, enum.Enum):
    HOMEWORK = "homework"
    QUIZ = "quiz"
    EXAM = "exam"
    PROJECT = "project"

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text)
    type = Column(String, nullable=False, default=AssignmentType.HOMEWORK) # Store as string for flexibility
    
    course_id = Column(String, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(String, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    
    due_date = Column(DateTime(timezone=True))
    max_score = Column(Integer, default=100)
    instructions = Column(Text)
    
    is_published = Column(Boolean, default=False)
    is_shared = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    course = relationship("Course", back_populates="assignments")
    teacher = relationship("User", foreign_keys=[teacher_id])
    attachments = relationship("AssignmentAttachment", back_populates="assignment", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")

class AssignmentAttachment(Base):
    __tablename__ = "assignment_attachments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    assignment_id = Column(String, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    
    type = Column(String, nullable=False) # 'file' or 'link'
    url = Column(String, nullable=False)
    file_name = Column(String)
    file_size = Column(Integer)
    mime_type = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    assignment = relationship("Assignment", back_populates="attachments")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    assignment_id = Column(String, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    content = Column(Text) # Text submission/notes
    file_url = Column(String) # URL from Supabase Cloud Storage
    
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", foreign_keys=[student_id])
    attachments = relationship("SubmissionAttachment", back_populates="submission", cascade="all, delete-orphan")
    grade = relationship("Grade", back_populates="submission", uselist=False, cascade="all, delete-orphan")

class SubmissionAttachment(Base):
    __tablename__ = "submission_attachments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    
    type = Column(String, nullable=False) # 'file' or 'link'
    url = Column(String, nullable=False)
    file_name = Column(String)
    file_size = Column(Integer)
    mime_type = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    submission = relationship("Submission", back_populates="attachments")

class Grade(Base):
    __tablename__ = "grades"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    score = Column(Integer, nullable=False)
    feedback = Column(Text)
    
    graded_at = Column(DateTime(timezone=True), server_default=func.now())
    graded_by = Column(String, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    # Relationships
    submission = relationship("Submission", back_populates="grade")
    grader = relationship("User", foreign_keys=[graded_by])
