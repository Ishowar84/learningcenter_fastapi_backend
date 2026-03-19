from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_db, get_current_active_user
from app.models.user import User, UserRole
from app.models.assignment import Assignment as AssignmentModel, Submission as SubmissionModel, Grade as GradeModel
from app.schemas.assignment import Submission as SubmissionSchema, GradeCreate, Grade as GradeSchema
from app.core.storage import storage_service

router = APIRouter()

@router.post("/", response_model=SubmissionSchema, status_code=status.HTTP_201_CREATED)
async def create_submission(
    assignment_id: str = Form(...),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new submission. Students only.
    If a file is provided, it's uploaded to cloud storage.
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can submit assignments")
    
    # Verify assignment exists and is published
    assignment = db.query(AssignmentModel).filter(
        AssignmentModel.id == assignment_id, 
        AssignmentModel.is_published == True
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found or not currently active")

    # Check if student already submitted (one submission per student per assignment)
    existing_submission = db.query(SubmissionModel).filter(
        SubmissionModel.assignment_id == assignment_id,
        SubmissionModel.student_id == current_user.id
    ).first()
    if existing_submission:
        raise HTTPException(status_code=400, detail="Assignment already submitted")

    file_url = None
    if file:
        file_url = await storage_service.upload_file(file, folder="submissions")

    new_submission = SubmissionModel(
        assignment_id=assignment_id,
        student_id=current_user.id,
        content=content,
        file_url=file_url
    )
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    return new_submission

@router.get("/", response_model=List[SubmissionSchema])
def read_submissions(
    assignment_id: Optional[str] = None,
    student_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Read submissions. 
    - Teachers see all submissions for an assignment.
    - Students see only their own.
    """
    query = db.query(SubmissionModel)
    
    if assignment_id:
        query = query.filter(SubmissionModel.assignment_id == assignment_id)
    if student_id:
        # Restriction: Students cannot see other students' submissions
        if current_user.role == UserRole.STUDENT and student_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        query = query.filter(SubmissionModel.student_id == student_id)
    elif current_user.role == UserRole.STUDENT:
        # Default for students if no student_id provided
        query = query.filter(SubmissionModel.student_id == current_user.id)
    
    # Restriction: Only assigned teacher or admin can see all assignment submissions
    if assignment_id and current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        # Student already filtered above by student_id or default
        pass
        
    return query.all()

@router.get("/{id}", response_model=SubmissionSchema)
def read_submission(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get submission by ID.
    Access Control: Student (own only), Admin/Teacher (all).
    """
    submission = db.query(SubmissionModel).filter(SubmissionModel.id == id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if current_user.role == UserRole.STUDENT and submission.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
        
    return submission
