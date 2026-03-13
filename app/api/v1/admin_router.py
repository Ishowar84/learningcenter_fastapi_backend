from fastapi import APIRouter, Depends
from app.api.deps import RoleChecker
from app.models.user_role import UserRole

router = APIRouter()

admin_check = RoleChecker([UserRole.ADMIN])

@router.get("/stats")
async def get_admin_stats(current_user: dict = Depends(admin_check)):
    return {
        "message": "Welcome, Administrator!",
        "stats": {
            "total_users": 100,
            "active_students": 85,
            "teachers": 10
        }
    }

@router.get("/settings")
async def get_admin_settings(current_user: dict = Depends(admin_check)):
    return {"system_status": "All systems operational", "version": "1.0.0"}
