from fastapi import APIRouter, Depends

from backend.schemas import EmployeeCreate
from backend.auth import verify_token, verify_admin
from backend.models import User
from backend.services import employee_service
router = APIRouter(
    tags=["Employees"]
)





# ==========================
# Create Employee
# ==========================


@router.post("/employees")
def create_employee(
    employee: EmployeeCreate,
    admin: User = Depends(verify_admin)
):
    return employee_service.create_employee(employee)

@router.get("/employee/dashboard")
def employee_dashboard(
    current_user: str = Depends(verify_token)
):
    return employee_service.employee_dashboard(
        current_user
    )
# ==========================
# Get All Employees
# ==========================
@router.get("/employees")
def get_employees(
    current_user: str = Depends(verify_token)
):
    return employee_service.get_employees()


# ==========================
# Employee Details
# IMPORTANT:
# This route MUST come before /employees/{employee_id}
# ==========================
@router.get("/employees/details")
def get_employee_details(
    current_user: str = Depends(verify_token)
):
    return employee_service.get_employee_details()

# ==========================
# Employees by Department
# IMPORTANT:
# This route MUST come before /employees/{employee_id}
# ==========================
@router.get("/employees/department/{department_id}")
def get_employees_by_department(
    department_id: int,
    current_user: str = Depends(verify_token)
):
    return employee_service.get_employees_by_department(department_id)
# ==========================
# Get Employee by ID
# MUST be after /details
# ==========================
@router.get("/employees/{employee_id}")
def get_employee(
    employee_id: int,
    current_user: str = Depends(verify_token)
):
    return employee_service.get_employee(employee_id)

# ==========================
# Update Employee
# ==========================
@router.put("/employees/{employee_id}")
def update_employee(
    employee_id: int,
    employee: EmployeeCreate,
    admin: User = Depends(verify_admin)
):
    return employee_service.update_employee(
        employee_id,
        employee
    )


# ==========================
# Delete Employee
# ==========================
@router.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: int,
    admin: User = Depends(verify_admin)
):
    return employee_service.delete_employee(employee_id)