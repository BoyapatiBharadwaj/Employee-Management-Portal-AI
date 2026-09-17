from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class SuperiorAssignmentCreate(BaseModel):
    superior_id: Optional[int] = None
    effective_from: date = Field(default_factory=date.today)


class MonthlyEvaluationCreate(BaseModel):
    employee_id: int
    performance_month: date
    rating: int = Field(ge=1, le=100)
    feedback: str = Field(min_length=1, max_length=5000)


class MonthlyPerformanceResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    department: Optional[str]
    superior_id: Optional[int]
    superior_name: Optional[str]
    performance_month: date
    superior_rating: Optional[int]
    feedback: Optional[str]
    attendance_score: Optional[float]
    leave_score: Optional[float]
    overall_score: Optional[float]
    rank: Optional[int]
    status: str


class PerformanceInsightsQuery(BaseModel):
    performance_month: Optional[date] = None
    department_id: Optional[int] = None
    superior_id: Optional[int] = None
    employee_id: Optional[int] = None
    rank: Optional[int] = None
