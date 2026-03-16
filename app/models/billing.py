import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, Integer, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class FeePlan(Base):
    __tablename__ = "fee_plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    rate_per_class = Column(Numeric(10, 2), nullable=False)
    billing_cycle = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_number = Column(String, unique=True, nullable=False)
    student_id = Column(String, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    parent_id = Column(String, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    fee_plan_id = Column(String, ForeignKey("fee_plans.id", ondelete="RESTRICT"), nullable=False)
    
    billing_period_start = Column(Date, nullable=False)
    billing_period_end = Column(Date, nullable=False)
    
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax = Column(Numeric(10, 2), default=0.00, nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="pending", nullable=False)
    due_date = Column(Date, nullable=False)
    paid_at = Column(DateTime(timezone=True))
    
    stripe_invoice_id = Column(String)
    notes = Column(Text)
    
    is_copy = Column(Boolean, default=False, nullable=False)
    original_invoice_id = Column(String, ForeignKey("invoices.id"))
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True))
    deleted_by = Column(String, ForeignKey("users.id"))
    deletion_reason = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(String, ForeignKey("invoices.id", ondelete="RESTRICT"), nullable=False)
    parent_id = Column(String, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="pending", nullable=False)
    payment_method = Column(String)
    
    stripe_payment_intent_id = Column(String)
    stripe_charge_id = Column(String)
    transaction_id = Column(String)
    failure_reason = Column(Text)
    
    paid_at = Column(DateTime(timezone=True))
    refunded_at = Column(DateTime(timezone=True))
    refund_amount = Column(Numeric(10, 2))
    notes = Column(Text)
    
    recorded_by_user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    verified_by_user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    verified_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
