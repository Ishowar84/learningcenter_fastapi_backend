from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User as UserModel
from app.models.user_role import UserRole
from app.services import enrollment_service
from app.schemas.enrollment import (
    EnrollmentRequest, 
    EnrollmentRequestCreate, 
    EnrollmentRequestUpdate,
    Enrollment
)

router = APIRouter()

@router.post("/request", response_model=EnrollmentRequest)
def create_enrollment_request(
    *,
    db: Session = Depends(deps.get_db),
    request_in: EnrollmentRequestCreate,
    current_user: UserModel = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new enrollment request. 
    Can be done by the student themselves, or an admin/parent on their behalf.
    """
    if current_user.role not in [UserRole.STUDENT, UserRole.PARENT, UserRole.ADMIN, UserRole.PARTNER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not enough permissions to request enrollment"
        )
    return enrollment_service.create_enrollment_request(db=db, request_in=request_in, requester=current_user)

@router.get("/my-requests", response_model=List[EnrollmentRequest])
def get_my_requests(
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_user),
) -> Any:
    """
    Get enrollment requests based on user role.
    Parents see requests they need to approve.
    """
    if current_user.role == UserRole.PARENT:
        return enrollment_service.get_enrollment_requests_for_parent(db=db, parent_id=current_user.id)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Endpoint primarily meant for parents. Admins use /courses/{course_id}/requests."
        )

@router.patch("/request/{request_id}", response_model=EnrollmentRequest)
def update_enrollment_request(
    *,
    db: Session = Depends(deps.get_db),
    request_id: str,
    update_data: EnrollmentRequestUpdate,
    current_user: UserModel = Depends(deps.get_current_user),
) -> Any:
    """
    Update an enrollment request status.
    Parents can approve -> "parent_approved"
    Admins can approve -> "admin_approved" (which finalizes the enrollment)
    """
    return enrollment_service.update_enrollment_request(db=db, request_id=request_id, update_data=update_data, current_user=current_user)

@router.get("/student/{student_id}", response_model=List[Enrollment])
def get_student_enrollments(
    *,
    db: Session = Depends(deps.get_db),
    student_id: str,
    current_user: UserModel = Depends(deps.get_current_user),
) -> Any:
    """
    Get finalized successful enrollments for a specific student.
    Must be the student themselves, their parent, or an admin.
    """
    return enrollment_service.get_enrollments_for_student(db=db, student_id=student_id)
