from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas import EmployeeCreate
from backend.auth import get_current_user, verify_admin
from backend.database import SessionLocal
from backend.models import User, Employee
from backend.services import employee_service
from backend.services.retention_service import retention_blocks_deletion

router = APIRouter(tags=["Employees"])


@router.post("/employees")
def create_employee(employee: EmployeeCreate, admin: User = Depends(verify_admin)):
    return employee_service.create_employee(employee)


@router.get("/employee/dashboard")
def employee_dashboard(current_user: User = Depends(get_current_user)):
    return employee_service.employee_dashboard(current_user.email)


@router.get("/employees")
def get_employees(admin: User = Depends(verify_admin)):
    return employee_service.get_employees()


@router.get("/employees/details")
def get_employee_details(admin: User = Depends(verify_admin)):
    return employee_service.get_employee_details()


@router.get("/employees/department/{department_id}")
def get_employees_by_department(department_id: int, admin: User = Depends(verify_admin)):
    return employee_service.get_employees_by_department(department_id)


@router.get("/employees/{employee_id}")
def get_employee(employee_id: int, current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        if current_user.role != "Admin":
            own = db.query(Employee).filter(Employee.email.ilike(current_user.email)).first()
            if not own or own.id != employee_id:
                raise HTTPException(status_code=403, detail="You can only view your own employee record")
        return employee_service.get_employee(employee_id)
    finally:
        db.close()


@router.put("/employees/{employee_id}")
def update_employee(employee_id: int, employee: EmployeeCreate, admin: User = Depends(verify_admin)):
    return employee_service.update_employee(employee_id, employee)


@router.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, admin: User = Depends(verify_admin)):
    db: Session = SessionLocal()
    try:
        if retention_blocks_deletion(db, employee_id):
            raise HTTPException(status_code=409, detail="Employee and related HR records are protected by the employment + 7-year retention policy")
    finally:
        db.close()
    return employee_service.delete_employee(employee_id)
