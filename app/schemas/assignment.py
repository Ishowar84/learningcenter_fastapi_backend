from typing import Optional, List
from datetime import datetime
from pydantic import Field
from .base import CamelModel
from app.models.assignment import AssignmentType

class AssignmentAttachmentBase(CamelModel):
    type: str
    url: str
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None

class AssignmentAttachmentCreate(AssignmentAttachmentBase):
    assignment_id: str

class AssignmentAttachment(AssignmentAttachmentBase):
    id: str
    assignment_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class AssignmentBase(CamelModel):
    title: str
    description: Optional[str] = None
    type: AssignmentType = AssignmentType.HOMEWORK
    due_date: Optional[datetime] = None
    max_score: int = 100
    instructions: Optional[str] = None
    is_published: bool = False
    is_shared: bool = True

class AssignmentCreate(AssignmentBase):
    course_id: str

class AssignmentUpdate(CamelModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[AssignmentType] = None
    due_date: Optional[datetime] = None
    max_score: Optional[int] = None
    instructions: Optional[str] = None
    is_published: Optional[bool] = None
    is_shared: Optional[bool] = None

class Assignment(AssignmentBase):
    id: str
    course_id: str
    teacher_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    attachments: List[AssignmentAttachment] = []

    class Config:
        from_attributes = True

class SubmissionAttachmentBase(CamelModel):
    type: str # 'file' or 'link'
    url: str
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None

class SubmissionAttachmentCreate(SubmissionAttachmentBase):
    submission_id: str

class SubmissionAttachment(SubmissionAttachmentBase):
    id: str
    submission_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class SubmissionBase(CamelModel):
    content: Optional[str] = None
    file_url: Optional[str] = None

class SubmissionCreate(SubmissionBase):
    assignment_id: str

class Submission(SubmissionBase):
    id: str
    assignment_id: str
    student_id: str
    submitted_at: datetime
    updated_at: Optional[datetime]
    attachments: List[SubmissionAttachment] = []

    class Config:
        from_attributes = True

class GradeBase(CamelModel):
    score: int
    feedback: Optional[str] = None

class GradeCreate(GradeBase):
    submission_id: str

class Grade(GradeBase):
    id: str
    submission_id: str
    graded_at: datetime
    graded_by: str

    class Config:
        from_attributes = True
