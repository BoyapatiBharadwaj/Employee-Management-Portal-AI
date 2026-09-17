from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import User, Employee, Department, Attendance, LeaveRequest, Payroll, Performance, EmployeeDocument, Onboarding, Offboarding
from backend.auth import verify_admin

router = APIRouter(tags=["Dashboard"])


def _dashboard_data(db: Session):
    payroll_records = db.query(Payroll).all()
    return {
        "total_users": db.query(User).count(),
        "total_employees": db.query(Employee).count(),
        "total_departments": db.query(Department).count(),
        "total_attendance": db.query(Attendance).count(),
        "total_leave_requests": db.query(LeaveRequest).count(),
        "approved_leaves": db.query(LeaveRequest).filter(LeaveRequest.status == "Approved").count(),
        "rejected_leaves": db.query(LeaveRequest).filter(LeaveRequest.status == "Rejected").count(),
        "pending_leaves": db.query(LeaveRequest).filter(LeaveRequest.status == "Pending").count(),
        "total_payroll_records": len(payroll_records),
        "total_salary_paid": sum(payroll.net_salary for payroll in payroll_records),
        "total_performance": db.query(Performance).count(),
        "total_documents": db.query(EmployeeDocument).count(),
        "total_onboarding": db.query(Onboarding).count(),
        "total_offboarding": db.query(Offboarding).count(),
    }


@router.get("/dashboard")
def dashboard(admin: User = Depends(verify_admin)):
    db: Session = SessionLocal()
    try:
        data = _dashboard_data(db)
        return {k: data[k] for k in ("total_users", "total_employees", "total_departments", "total_attendance")}
    finally:
        db.close()


@router.get("/dashboard/analytics")
def dashboard_analytics(admin: User = Depends(verify_admin)):
    db: Session = SessionLocal()
    try:
        return _dashboard_data(db)
    finally:
        db.close()
