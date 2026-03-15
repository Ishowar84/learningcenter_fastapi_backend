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
        # Define base users for each role
        mock_users = [
            {"email": "admin@example.com", "role": UserRole.ADMIN, "first_name": "Admin", "last_name": "User"},
            {"email": "student@example.com", "role": UserRole.STUDENT, "first_name": "Student", "last_name": "Test"},
            {"email": "parent@example.com", "role": UserRole.PARENT, "first_name": "Parent", "last_name": "Test"},
            {"email": "teacher@example.com", "role": UserRole.TEACHER, "first_name": "Teacher", "last_name": "Test"},
            {"email": "finance@example.com", "role": UserRole.FINANCE_ADMIN, "first_name": "Finance", "last_name": "Admin"},
            {"email": "partner@example.com", "role": UserRole.PARTNER_ADMIN, "first_name": "Partner", "last_name": "Admin"},
        ]

        default_password = get_password_hash("password")

        for user_data in mock_users:
            email = user_data["email"]
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    id=str(uuid.uuid4()),
                    email=email,
                    password=default_password,
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    name=f"{user_data['first_name']} {user_data['last_name']}",
                    role=user_data["role"],
                    is_active=True
                )
                db.add(user)
                print(f"✅ Created mock user: {email} ({user_data['role'].value})")
            else:
                print(f"ℹ️ User already exists: {email}")
        
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
