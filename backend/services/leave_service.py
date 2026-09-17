from unittest import result

from sqlalchemy.orm import Session
from datetime import datetime

from backend.database import SessionLocal
from backend.models import LeaveRequest, Employee, User


def apply_leave(leave):

    db: Session = SessionLocal()

    try:

        employee = db.query(Employee).filter(
            Employee.id == leave.employee_id
        ).first()

        if employee is None:
            return {
                "message": "Employee not found"
            }

        new_leave = LeaveRequest(
            employee_id=leave.employee_id,
            leave_type=leave.leave_type,
            start_date=datetime.strptime(
                leave.start_date,
                "%Y-%m-%d"
            ).date(),
            end_date=datetime.strptime(
                leave.end_date,
                "%Y-%m-%d"
            ).date(),
            reason=leave.reason,
            status="Pending"
        )

        db.add(new_leave)
        db.commit()
        db.refresh(new_leave)

        return {
            "message": "Leave request submitted successfully",
            "leave": new_leave
        }

    except Exception as e:

        db.rollback()

        return {
            "error": str(e)
        }

    finally:
        db.close()


def get_leave_requests():

    db: Session = SessionLocal()

    try:

        leaves = db.query(LeaveRequest).all()

        result = []

        for leave in leaves:

            result.append({

                "id": leave.id,
                "employee_id": leave.employee_id,
                "employee_name": leave.employee.full_name,
                "leave_type": leave.leave_type,
                "start_date": str(leave.start_date),
                "end_date": str(leave.end_date),
                "reason": leave.reason,
                "status": leave.status

            })

        return result

    finally:
        db.close()


def approve_leave(leave_id):

    db: Session = SessionLocal()

    try:

        leave = db.query(LeaveRequest).filter(
            LeaveRequest.id == leave_id
        ).first()

        if leave is None:
            return {
                "message": "Leave request not found"
            }

        leave.status = "Approved"

        db.commit()
        db.refresh(leave)

        return {
            "message": "Leave approved successfully",
            "leave": leave
        }

    finally:
        db.close()


def reject_leave(leave_id):

    db: Session = SessionLocal()

    try:

        leave = db.query(LeaveRequest).filter(
            LeaveRequest.id == leave_id
        ).first()

        if leave is None:
            return {
                "message": "Leave request not found"
            }

        leave.status = "Rejected"

        db.commit()
        db.refresh(leave)

        return {
            "message": "Leave rejected successfully",
            "leave": leave
        }

    finally:
        db.close()


def get_my_leaves(email):

    db: Session = SessionLocal()

    try:

        employee = db.query(Employee).filter(
            Employee.email == email
        ).first()

        if employee is None:
            return []

        result = []

        for leave in db.query(LeaveRequest).filter(
    LeaveRequest.employee_id == employee.id
).all():

            result.append({

        "id": leave.id,

        "leave_type": leave.leave_type,

        "start_date": str(leave.start_date),

        "end_date": str(leave.end_date),

        "reason": leave.reason,

        "status": leave.status

    })
        return result

    finally:
        db.close()


def cancel_leave(leave_id):

    db: Session = SessionLocal()

    try:

        leave = db.query(LeaveRequest).filter(
            LeaveRequest.id == leave_id
        ).first()

        if leave is None:
            return {
                "message": "Leave not found"
            }

        if leave.status in {"Approved", "Rejected"}:
            return {"message": "Processed leave requests cannot be cancelled."}
        leave.status = "Cancelled"
        db.commit()

        return {
            "message": "Leave cancelled successfully"
        }

    finally:
        db.close()