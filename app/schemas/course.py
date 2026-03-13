from typing import Optional, List
from pydantic import BaseModel

# Subject Schemas
class SubjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(SubjectBase):
    name: Optional[str] = None

class Subject(SubjectBase):
    id: int

    class Config:
        from_attributes = True

# Course Schemas
class CourseBase(BaseModel):
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

    class Config:
        from_attributes = True
        
class CourseWithSubject(Course):
    subject: Subject
