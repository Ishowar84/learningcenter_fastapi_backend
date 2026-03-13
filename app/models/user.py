from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from app.db.session import Base
from app.models.user_role import UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    full_name = Column(String)
