from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.course import Course
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.course import Course as CourseSchema, CourseCreate, CourseUpdate
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

router = APIRouter()

# Role checkers
admin_or_teacher_check = deps.RoleChecker([UserRole.ADMIN, UserRole.TEACHER, UserRole.PARTNER_ADMIN])
optional_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

async def get_optional_user(db: Session = Depends(deps.get_db), token: str = Depends(optional_oauth2)) -> Optional[User]:
    if not token:
        return None
    try:
        from jose import jwt, JWTError
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id:
            return db.query(User).filter(User.id == user_id).first()
    except Exception:
        pass
    return None

@router.get("/", response_model=List[CourseSchema])
async def read_courses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[User] = Depends(get_optional_user),
    teacher_id: Optional[str] = None
):
    """
    Retrieve courses. Results change based on user role:
    - Admin/Partner Admin sees all courses
    - Teachers see courses they teach or are published
    - Students/Parents and Unauthenticated users see published courses
    """
    query = db.query(Course)
    
    # If filtered by a specific teacher
    if teacher_id:
        query = query.filter(Course.teacher_id == teacher_id)
        
    # Role-based visibility
    if current_user and current_user.role == UserRole.TEACHER:
        # Teachers see their own courses OR active courses
        query = query.filter((Course.teacher_id == current_user.id) | (Course.is_active == True))
    elif not current_user or current_user.role in [UserRole.STUDENT, UserRole.PARENT]:
        # Unauthenticated users, Students and Parents only see active courses
        query = query.filter(Course.is_active == True)
        
    courses = query.offset(skip).limit(limit).all()
    return courses

@router.get("/{course_id}", response_model=CourseSchema)
async def read_course(
    course_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get course by ID
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # If student/parent, ensure the course is active or they are enrolled (enrollment check to be added)
    if current_user.role in [UserRole.STUDENT, UserRole.PARENT] and not course.is_active:
        raise HTTPException(status_code=403, detail="Don't have permission to view this inactive course")
        
    return course

@router.post("/", response_model=CourseSchema, status_code=status.HTTP_201_CREATED)
async def create_course(
    *,
    db: Session = Depends(deps.get_db),
    course_in: CourseCreate,
    current_user: User = Depends(admin_or_teacher_check)
):
    """
    Create new course. Teachers and Admins only.
    """
    course_data = course_in.dict()
    # If a teacher is creating the course and didn't specify a teacher_id, default to themselves
    if current_user.role == UserRole.TEACHER and not course_data.get("teacher_id"):
        course_data["teacher_id"] = current_user.id
        
    db_course = Course(**course_data)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.put("/{course_id}", response_model=CourseSchema)
async def update_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: str,
    course_in: CourseUpdate,
    current_user: User = Depends(admin_or_teacher_check)
):
    """
    Update a course. Admins can update any, teachers can update their own.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Security: Teacher can only update their own courses
    if current_user.role == UserRole.TEACHER and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to edit this course")
        
    update_data = course_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(course, field, value)
        
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: str,
    current_user: User = Depends(admin_or_teacher_check)
):
    """
    Delete a course. Admins can delete any, teachers can delete their own.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    if current_user.role == UserRole.TEACHER and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to delete this course")
        
    db.delete(course)
    db.commit()
    return None
