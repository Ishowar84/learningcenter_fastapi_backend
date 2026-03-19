from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_db, get_current_active_user
from app.models.user import User, UserRole
from app.models.assignment import Assignment as AssignmentModel, Submission as SubmissionModel, Grade as GradeModel, SubmissionAttachment as SubmissionAttachmentModel
from app.schemas.assignment import Submission as SubmissionSchema, GradeCreate, Grade as GradeSchema, SubmissionAttachmentCreate
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

@router.post("/attachments/upload")
async def upload_submission_attachment(
    file: UploadFile = File(...),
    assignment_id: Optional[str] = Form(None),
    student_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Step 1 of Multi-step upload: Just upload file and return path.
    """
    # Authorization: Student uploading for themselves?
    if current_user.role == UserRole.STUDENT and student_id and student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot upload for another student")
    
    file_url = await storage_service.upload_file(file, folder="submissions")
    
    # Return what the frontend expects: objectPath, fileSize, mimeType
    return {
        "objectPath": file_url,
        "fileSize": file.size,
        "mimeType": file.content_type
    }

@router.post("/{id}/attachments", response_model=SubmissionSchema)
async def add_submission_attachment(
    id: str,
    attachment: SubmissionAttachmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Step 3 of Multi-step upload: Associate attachment with submission.
    """
    submission = db.query(SubmissionModel).filter(SubmissionModel.id == id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Authorization
    if current_user.role == UserRole.STUDENT and submission.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    new_attachment = SubmissionAttachmentModel(
        submission_id=id,
        type=attachment.type,
        url=attachment.url,
        file_name=attachment.file_name,
        file_size=attachment.file_size,
        mime_type=attachment.mime_type
    )
    db.add(new_attachment)
    db.commit()
    db.refresh(submission)
    return submission

# Grading Endpoint (Centralized here for now)
@router.post("/grades", response_model=GradeSchema)
async def create_grade(
    grade: GradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create or update a grade for a submission. Teachers/Admins only.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(status_code=403, detail="Only teachers or admins can grade submissions")
    
    # Check if submission exists
    submission = db.query(SubmissionModel).filter(SubmissionModel.id == grade.submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Check if grade already exists (update it)
    existing_grade = db.query(GradeModel).filter(GradeModel.submission_id == grade.submission_id).first()
    if existing_grade:
        existing_grade.score = grade.score
        existing_grade.feedback = grade.feedback
        existing_grade.graded_by = current_user.id
        db.commit()
        db.refresh(existing_grade)
        return existing_grade
    
    new_grade = GradeModel(
        submission_id=grade.submission_id,
        score=grade.score,
        feedback=grade.feedback,
        graded_by=current_user.id
    )
    db.add(new_grade)
    db.commit()
    db.refresh(new_grade)
    return new_grade

# Assignment Grading View (Specific list for teachers)
@router.get("/assignments/{assignment_id}/grading", response_model=List[SubmissionSchema])
def get_submissions_for_grading(
    assignment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Returns all submissions for an assignment with student details (for grading).
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    submissions = db.query(SubmissionModel).filter(
        SubmissionModel.assignment_id == assignment_id
    ).all()
    
    return submissions
