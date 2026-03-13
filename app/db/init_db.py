import uuid
from app.db.session import engine, Base, SessionLocal
from app.models.user import User
from app.models.user_role import UserRole
from app.core.security import get_password_hash

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create an initial admin user if it doesn't exist
        admin_email = "admin@example.com"
        user = db.query(User).filter(User.email == admin_email).first()
        if not user:
            user = User(
                id=str(uuid.uuid4()),
                email=admin_email,
                password=get_password_hash("password"),
                first_name="Admin",
                last_name="User",
                name="Admin User",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(user)
            db.commit()
            print(f"Initial admin user created: {admin_email}")
        else:
            print("Admin user already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
