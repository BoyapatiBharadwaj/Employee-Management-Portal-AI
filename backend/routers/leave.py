from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas import LeaveRequestCreate
from backend.auth import get_current_user, verify_admin
from backend.database import SessionLocal
from backend.models import User, Employee, LeaveRequest
from backend.services import leave_service

router = APIRouter(tags=["Leave Management"])


@router.post("/leave/apply")
def apply_leave(leave: LeaveRequestCreate, current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        employee = db.query(Employee).filter(Employee.email.ilike(current_user.email)).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee profile not found")
        leave.employee_id = employee.id
        return leave_service.apply_leave(leave)
    finally:
        db.close()


@router.get("/leave/me")
def my_leaves(current_user: User = Depends(get_current_user)):
    return leave_service.get_my_leaves(current_user.email)


@router.delete("/leave/{leave_id}")
def cancel_leave(leave_id: int, current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        row = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="Leave request not found")
        employee = db.query(Employee).filter(Employee.email.ilike(current_user.email)).first()
        if current_user.role != "Admin" and (not employee or row.employee_id != employee.id):
            raise HTTPException(status_code=403, detail="You can only cancel your own leave requests")
        return leave_service.cancel_leave(leave_id)
    finally:
        db.close()


@router.get("/leave")
def get_leave_requests(admin: User = Depends(verify_admin)):
    return leave_service.get_leave_requests()


@router.put("/leave/approve/{leave_id}")
def approve_leave(leave_id: int, admin: User = Depends(verify_admin)):
    return leave_service.approve_leave(leave_id)


@router.put("/leave/reject/{leave_id}")
def reject_leave(leave_id: int, admin: User = Depends(verify_admin)):
    return leave_service.reject_leave(leave_id)
