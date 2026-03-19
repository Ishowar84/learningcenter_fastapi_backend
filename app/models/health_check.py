import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class UptimeLog(Base):
    __tablename__ = "uptime_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    called_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
