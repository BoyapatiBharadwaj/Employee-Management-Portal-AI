from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.auth import get_current_user, verify_admin
from backend.database import SessionLocal
from backend.models import User, Employee, Attendance
from backend.services import attendance_service

router = APIRouter(tags=["Attendance"])


@router.post("/attendance/check-in")
def check_in(current_user: User = Depends(get_current_user)):
    return attendance_service.check_in(current_user.email)


@router.put("/attendance/check-out")
def check_out(current_user: User = Depends(get_current_user)):
    return attendance_service.check_out(current_user.email)


@router.get("/attendance/me")
def my_attendance(current_user: User = Depends(get_current_user)):
    return attendance_service.my_attendance(current_user.email)


@router.get("/attendance/my-summary")
def my_summary(current_user: User = Depends(get_current_user)):
    return attendance_service.my_summary(current_user.email)


@router.get("/attendance/analytics")
def attendance_analytics(admin: User = Depends(verify_admin)):
    return attendance_service.attendance_analytics()


@router.get("/attendance")
def get_all_attendance(admin: User = Depends(verify_admin)):
    return attendance_service.get_all_attendance()


@router.put("/attendance/{attendance_id}")
def update_attendance(attendance_id: int, check_in: str, check_out: str, admin: User = Depends(verify_admin)):
    return attendance_service.update_attendance(attendance_id, check_in, check_out)


@router.get("/attendance/{employee_id}")
def get_employee_attendance(employee_id: int, current_user: User = Depends(get_current_user)):
    if current_user.role == "Admin":
        return attendance_service.get_employee_attendance(employee_id)
    db: Session = SessionLocal()
    try:
        own = db.query(Employee).filter(Employee.email.ilike(current_user.email)).first()
        if not own or own.id != employee_id:
            raise HTTPException(status_code=403, detail="You can only view your own attendance")
        return attendance_service.get_employee_attendance(employee_id)
    finally:
        db.close()
