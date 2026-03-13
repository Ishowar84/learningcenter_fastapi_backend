from typing import Optional
from app.schemas.base import CamelModel

# Subject Schemas
class SubjectBase(CamelModel):
    name: str
    description: Optional[str] = None

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(SubjectBase):
    name: Optional[str] = None

class Subject(SubjectBase):
    id: int

# Course Schemas
class CourseBase(CamelModel):
    title: str
    description: Optional[str] = None
    grade_level: Optional[str] = None
    subject_id: int

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    title: Optional[str] = None
    subject_id: Optional[int] = None

class Course(CourseBase):
    id: int
    teacher_id: Optional[int] = None
        
class CourseWithSubject(Course):
    subject: Subject
