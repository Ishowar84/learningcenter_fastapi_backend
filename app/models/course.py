from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    
    courses = relationship("Course", back_populates="subject")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    grade_level = Column(String)  # e.g., "KG", "Grade 1", etc.
    
    subject = relationship("Subject", back_populates="courses")
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # We'll add relationships to users later when we have more models
