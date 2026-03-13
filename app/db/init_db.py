from app.db.session import engine, Base
from app.models.user import User
from app.models.course import Subject, Course
from app.models.user_role import UserRole
from app.db.session import SessionLocal
from app.services import user_service
from app.schemas.user import UserCreate

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create an initial admin user if it doesn't exist
    db = SessionLocal()
    try:
        user = user_service.get_user_by_email(db, email="admin@example.com")
        if not user:
            user_in = UserCreate(
                email="admin@example.com",
                password="password",
                full_name="Admin User",
                role=UserRole.ADMIN
            )
            user_service.create_user(db, user_in=user_in)
            print("Initial admin user created.")
        else:
            print("Admin user already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
