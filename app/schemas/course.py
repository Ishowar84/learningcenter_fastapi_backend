from typing import Optional, List, Dict, Any
from datetime import date, datetime
from app.schemas.base import CamelModel
from app.schemas.user import User

# Subject Schemas
class SubjectBase(CamelModel):
    name: str
    description: Optional[str] = None
    grade: Optional[str] = None

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(CamelModel):
    name: Optional[str] = None
    description: Optional[str] = None
    grade: Optional[str] = None

class Subject(SubjectBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Course Schemas
class CourseBase(CamelModel):
    title: str
    description: Optional[str] = None
    subject: str
    grade: str
    start_date: Optional[date] = None
    duration: Optional[str] = None
    philosophy: Optional[str] = None
    prerequisites: Optional[str] = None
    learning_objectives: Optional[str] = None
    curriculum: Optional[List[Dict[str, str]]] = []
    practical_sessions: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_active: bool = False

class CourseCreate(CourseBase):
    teacher_id: Optional[str] = None

class CourseUpdate(CamelModel):
    title: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    grade: Optional[str] = None
    start_date: Optional[date] = None
    duration: Optional[str] = None
    philosophy: Optional[str] = None
    prerequisites: Optional[str] = None
    learning_objectives: Optional[str] = None
    curriculum: Optional[List[Dict[str, str]]] = None
    practical_sessions: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_active: Optional[bool] = None
    teacher_id: Optional[str] = None

class Course(CourseBase):
    id: str
    teacher_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CourseWithTeacher(Course):
    teacher: Optional[User] = None
