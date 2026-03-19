from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_db, get_current_active_user
from app.models.user import User, UserRole
from app.models.assignment import Assignment as AssignmentModel
from app.models.course import Course as CourseModel
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate, Assignment as AssignmentSchema
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=AssignmentSchema, status_code=status.HTTP_201_CREATED)
def create_assignment(
    assignment_in: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new assignment. Only teachers and admins can create assignments.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Verify course exists
    course = db.query(CourseModel).filter(CourseModel.id == assignment_in.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    new_assignment = AssignmentModel(
        **assignment_in.model_dump(),
        teacher_id=current_user.id
    )
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment

@router.get("/", response_model=List[AssignmentSchema])
def read_assignments(
    course_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all assignments. Can be filtered by course_id.
    """
    query = db.query(AssignmentModel)
    if course_id:
        query = query.filter(AssignmentModel.course_id == course_id)
    
    # Basic filtering logic: Students only see published assignments
    if current_user.role == UserRole.STUDENT:
        query = query.filter(AssignmentModel.is_published == True)
        
    return query.all()

@router.get("/{id}", response_model=AssignmentSchema)
def read_assignment(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get assignment by ID.
    """
    assignment = db.query(AssignmentModel).filter(AssignmentModel.id == id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Students cannot see unpublished assignments
    if current_user.role == UserRole.STUDENT and not assignment.is_published:
        raise HTTPException(status_code=403, detail="Assignment not accessible")
        
    return assignment

@router.patch("/{id}", response_model=AssignmentSchema)
def update_assignment(
    id: str,
    assignment_in: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an assignment.
    """
    assignment = db.query(AssignmentModel).filter(AssignmentModel.id == id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    if current_user.role != UserRole.ADMIN and assignment.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = assignment_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assignment, field, value)
    
    db.commit()
    db.refresh(assignment)
    return assignment

@router.delete("/{id}", response_model=AssignmentSchema)
def delete_assignment(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an assignment.
    """
    assignment = db.query(AssignmentModel).filter(AssignmentModel.id == id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    if current_user.role != UserRole.ADMIN and assignment.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(assignment)
    db.commit()
    return assignment
