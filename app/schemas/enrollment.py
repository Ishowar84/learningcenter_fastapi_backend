from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.base import CamelModel
from app.schemas.user import User

class EnrollmentRequestBase(CamelModel):
    course_id: str
    student_id: str
    parent_id: str
    notes: Optional[str] = None

class EnrollmentRequestCreate(EnrollmentRequestBase):
    pass

class EnrollmentRequestUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Must be 'parent_approved', 'admin_approved', or 'rejected'")
    rejection_reason: Optional[str] = None

class EnrollmentRequestInDBBase(EnrollmentRequestBase):
    id: str
    status: str
    requested_at: datetime
    parent_approved_at: Optional[datetime] = None
    admin_approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class EnrollmentRequest(EnrollmentRequestInDBBase):
    student: Optional[User] = None

class EnrollmentBase(CamelModel):
    course_id: str
    student_id: str

class EnrollmentCreate(EnrollmentBase):
    approval_status: str = "pending"

class EnrollmentUpdate(BaseModel):
    approval_status: Optional[str] = None
    rejection_reason: Optional[str] = None

class EnrollmentInDBBase(EnrollmentBase):
    id: str
    approval_status: str
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    enrolled_at: datetime
    
    class Config:
        from_attributes = True

class Enrollment(EnrollmentInDBBase):
    student: Optional[User] = None
