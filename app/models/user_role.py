from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"
    ADMIN = "admin"
    FINANCE_ADMIN = "finance_admin"
    PARTNER_ADMIN = "partner_admin"
