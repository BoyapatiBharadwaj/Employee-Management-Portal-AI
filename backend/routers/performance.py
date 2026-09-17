from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas import PerformanceCreate
from backend.auth import get_current_user, verify_admin
from backend.database import SessionLocal
from backend.models import User, Employee, Performance
from backend.services import performance_service
from backend.services.retention_service import retention_blocks_deletion

router = APIRouter(tags=["Performance Management"])


@router.post("/performance")
def create_performance(performance: PerformanceCreate, admin: User = Depends(verify_admin)):
    return performance_service.create_performance(performance)


@router.get("/performance")
def get_performance(admin: User = Depends(verify_admin)):
    return performance_service.get_performance()


@router.get("/performance/me")
def my_performance(current_user: User = Depends(get_current_user)):
    return performance_service.get_my_performance(current_user.email)


@router.get("/performance/{employee_id}")
def get_employee_performance(employee_id: int, current_user: User = Depends(get_current_user)):
    if current_user.role == "Admin":
        return performance_service.get_employee_performance(employee_id)
    db: Session = SessionLocal()
    try:
        own = db.query(Employee).filter(Employee.email.ilike(current_user.email)).first()
        if own and own.id == employee_id:
            return performance_service.get_employee_performance(employee_id)
        if current_user.role in {"Superior", "CEO"} and own:
            target = db.query(Employee).filter(Employee.id == employee_id).first()
            if target and target.superior_id == own.id:
                return performance_service.get_employee_performance(employee_id)
        raise HTTPException(status_code=403, detail="You do not have access to this employee's performance")
    finally:
        db.close()


@router.delete("/performance/{review_id}")
def delete_performance(review_id: int, admin: User = Depends(verify_admin)):
    db: Session = SessionLocal()
    try:
        review = db.query(Performance).filter(Performance.id == review_id).first()
        if review and retention_blocks_deletion(db, review.employee_id):
            raise HTTPException(status_code=409, detail="Performance history is protected by the employment + 7-year retention policy")
    finally:
        db.close()
    return performance_service.delete_performance(review_id)
