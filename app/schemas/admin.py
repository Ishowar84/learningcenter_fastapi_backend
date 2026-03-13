from app.schemas.base import CamelModel

class AdminStats(CamelModel):
    total_users: int
    active_students: int
    teachers: int

class AdminStatsResponse(CamelModel):
    message: str
    stats: AdminStats

class AdminSettingsResponse(CamelModel):
    system_status: str
    version: str
