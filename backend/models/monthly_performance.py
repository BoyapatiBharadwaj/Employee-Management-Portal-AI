from datetime import datetime, timezone
from sqlalchemy import CheckConstraint, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.database import Base


class MonthlyPerformance(Base):
    __tablename__ = "monthly_performance"
    __table_args__ = (
        UniqueConstraint("employee_id", "performance_month", name="uq_employee_performance_month"),
        CheckConstraint("superior_rating IS NULL OR (superior_rating >= 1 AND superior_rating <= 100)", name="ck_mp_rating_1_100"),
        CheckConstraint("attendance_score IS NULL OR (attendance_score >= 0 AND attendance_score <= 100)", name="ck_mp_attendance_0_100"),
        CheckConstraint("leave_score IS NULL OR (leave_score >= 0 AND leave_score <= 100)", name="ck_mp_leave_0_100"),
        CheckConstraint("overall_score IS NULL OR (overall_score >= 0 AND overall_score <= 100)", name="ck_mp_overall_0_100"),
    )

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    superior_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True)
    performance_month = Column(Date, nullable=False, index=True)
    superior_rating = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)

    # Immutable calculation snapshot inputs retained for historical transparency.
    attendance_present_days = Column(Integer, nullable=True)
    attendance_absent_days = Column(Integer, nullable=True)
    attendance_late_days = Column(Integer, nullable=True)
    attendance_late_minutes = Column(Integer, nullable=True)
    attendance_scheduled_days = Column(Integer, nullable=True)
    leave_request_count = Column(Integer, nullable=True)
    leave_approved_days = Column(Integer, nullable=True)
    leave_rejected_days = Column(Integer, nullable=True)
    leave_unplanned_days = Column(Integer, nullable=True)
    leave_percentage = Column(Float, nullable=True)

    attendance_score = Column(Float, nullable=True)
    leave_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True, index=True)
    rank = Column(Integer, nullable=True)
    status = Column(String(30), nullable=False, default="Pending Review")
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    corrected_at = Column(DateTime(timezone=True), nullable=True)
    correction_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    employee = relationship("Employee", foreign_keys=[employee_id])
    superior = relationship("Employee", foreign_keys=[superior_id])
