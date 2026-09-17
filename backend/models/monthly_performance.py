from datetime import datetime, timezone
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.database import Base


class MonthlyPerformance(Base):
    __tablename__ = "monthly_performance"
    __table_args__ = (UniqueConstraint("employee_id", "performance_month", name="uq_employee_performance_month"),)

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    superior_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True)
    performance_month = Column(Date, nullable=False, index=True)
    superior_rating = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    attendance_score = Column(Float, nullable=True)
    leave_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True, index=True)
    rank = Column(Integer, nullable=True)
    status = Column(String(30), nullable=False, default="Pending Review")
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", foreign_keys=[employee_id])
    superior = relationship("Employee", foreign_keys=[superior_id])
