from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException, status

from app.models.enrollment import Enrollment, EnrollmentRequest
from app.models.course import Course
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.enrollment import EnrollmentRequestCreate, EnrollmentRequestUpdate, EnrollmentCreate, EnrollmentUpdate


def get_enrollments_for_student(db: Session, student_id: str) -> List[Enrollment]:
    """Get all enrollments for a specific student."""
    return db.query(Enrollment).filter(Enrollment.student_id == student_id).all()

def get_enrollment_requests_for_parent(db: Session, parent_id: str) -> List[EnrollmentRequest]:
    """Get all enrollment requests sent to a specific parent."""
    return db.query(EnrollmentRequest).filter(EnrollmentRequest.parent_id == parent_id).all()

def get_enrollment_requests_for_course(db: Session, course_id: str) -> List[EnrollmentRequest]:
    """Get all enrollment requests for a specific course (admin view)."""
    return db.query(EnrollmentRequest).filter(EnrollmentRequest.course_id == course_id).all()

def create_enrollment_request(db: Session, request_in: EnrollmentRequestCreate, requester: User) -> EnrollmentRequest:
    """Create a new enrollment request."""
    # Ensure neither the student nor the course are bogus
    student = db.query(User).filter(User.id == request_in.student_id).first()
    course = db.query(Course).filter(Course.id == request_in.course_id).first()
    parent = db.query(User).filter(User.id == request_in.parent_id).first()
    
    if not student or not course or not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student, Course, or Parent not found"
        )

    # Check for existing request
    existing_request = db.query(EnrollmentRequest).filter(
        EnrollmentRequest.student_id == request_in.student_id,
        EnrollmentRequest.course_id == request_in.course_id
    ).first()
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An enrollment request for this student and course already exists."
        )

    db_obj = EnrollmentRequest(
        course_id=request_in.course_id,
        student_id=request_in.student_id,
        parent_id=request_in.parent_id,
        notes=request_in.notes,
        status="requested"
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_enrollment_request(
    db: Session, 
    request_id: str, 
    update_data: EnrollmentRequestUpdate,
    current_user: User
) -> EnrollmentRequest:
    """Approve or reject an enrollment request based on the user's role."""
    enrollment_request = db.query(EnrollmentRequest).filter(EnrollmentRequest.id == request_id).first()
    if not enrollment_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment request not found")

    new_status = update_data.status
    
    # Parent approval path
    if current_user.role == UserRole.PARENT and current_user.id == enrollment_request.parent_id:
        if new_status == "parent_approved":
            enrollment_request.status = "parent_approved"
            enrollment_request.parent_approved_at = datetime.utcnow()
        elif new_status == "rejected":
            enrollment_request.status = "rejected"
            enrollment_request.rejected_at = datetime.utcnow()
            enrollment_request.rejection_reason = update_data.rejection_reason
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status change for parent")
    
    # Admin approval path
    elif current_user.role in [UserRole.ADMIN, UserRole.PARTNER_ADMIN]:
        if new_status == "admin_approved" and enrollment_request.status in ["parent_approved", "requested"]:
            enrollment_request.status = "admin_approved"
            enrollment_request.admin_approved_at = datetime.utcnow()
            
            # Automatically create the final enrollment row upon admin approval
            final_enrollment = Enrollment(
                course_id=enrollment_request.course_id,
                student_id=enrollment_request.student_id,
                approval_status="approved",
                approved_at=datetime.utcnow()
            )
            db.add(final_enrollment)
            
        elif new_status == "rejected":
            enrollment_request.status = "rejected"
            enrollment_request.rejected_at = datetime.utcnow()
            enrollment_request.rejection_reason = update_data.rejection_reason
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status change for admin")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this request")

    enrollment_request.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(enrollment_request)
    return enrollment_request
