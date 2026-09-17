from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import Employee
from backend.models import Attendance, LeaveRequest, Payroll, Performance, User
from sqlalchemy import func
from datetime import date

def create_employee(employee):

    db: Session = SessionLocal()

    try:

        new_employee = Employee(
            employee_id=employee.employee_id,
            full_name=employee.full_name,
            email=employee.email,
            department_id=employee.department_id,
            designation=employee.designation,
            salary=employee.salary
        )

        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)

        return {
            "message": "Employee created successfully",
            "employee": new_employee
        }

    except Exception as e:

        db.rollback()

        return {
            "error": str(e)
        }

    finally:
        db.close()


def get_employees():

    db: Session = SessionLocal()

    try:
        employees = db.query(Employee).all()
        result = []
        for emp in employees:
            user = db.query(User).filter(User.email.ilike(emp.email)).first()
            result.append({
                "id": emp.id,
                "employee_id": emp.employee_id,
                "full_name": emp.full_name,
                "email": emp.email,
                "department_id": emp.department_id,
                "department_name": emp.department.department_name if emp.department else None,
                "designation": emp.designation,
                "salary": emp.salary,
                "superior_id": emp.superior_id,
                "superior_name": emp.superior.full_name if emp.superior else None,
                "user_role": user.role if user else None,
            })
        return result

    finally:
        db.close()


def get_employee_details():

    db: Session = SessionLocal()

    try:

        employees = db.query(Employee).all()

        data = []

        for emp in employees:

            data.append({

                "id": emp.id,
                "employee_id": emp.employee_id,
                "full_name": emp.full_name,
                "email": emp.email,
                "department": emp.department.department_name,
                "designation": emp.designation,
                "salary": emp.salary

            })

        return data

    finally:
        db.close()
def get_employees_by_department(department_id):

    db: Session = SessionLocal()

    try:

        employees = db.query(Employee).filter(
            Employee.department_id == department_id
        ).all()

        if not employees:
            return {
                "message": "No employees found in this department"
            }

        result = []

        for emp in employees:

            result.append({

                "employee_id": emp.employee_id,
                "full_name": emp.full_name,
                "email": emp.email,
                "department": emp.department.department_name,
                "designation": emp.designation,
                "salary": emp.salary

            })

        return result

    finally:
        db.close()


def get_employee(employee_id):

    db: Session = SessionLocal()

    try:

        employee = db.query(Employee).filter(
            Employee.id == employee_id
        ).first()

        if employee is None:
            return {
                "message": "Employee not found"
            }

        return employee

    finally:
        db.close()


def update_employee(employee_id, employee):

    db: Session = SessionLocal()

    try:

        existing_employee = db.query(Employee).filter(
            Employee.id == employee_id
        ).first()

        if existing_employee is None:
            return {
                "message": "Employee not found"
            }

        existing_employee.employee_id = employee.employee_id
        existing_employee.full_name = employee.full_name
        existing_employee.email = employee.email
        existing_employee.department_id = employee.department_id
        existing_employee.designation = employee.designation
        existing_employee.salary = employee.salary

        db.commit()
        db.refresh(existing_employee)

        return {
            "message": "Employee updated successfully",
            "employee": existing_employee
        }

    finally:
        db.close()


def delete_employee(employee_id):

    db: Session = SessionLocal()

    try:

        employee = db.query(Employee).filter(
            Employee.id == employee_id
        ).first()

        if employee is None:
            return {
                "message": "Employee not found"
            }

        db.delete(employee)
        db.commit()

        return {
            "message": "Employee deleted successfully"
        }

    finally:
        db.close()

def employee_dashboard(current_user):

    db: Session = SessionLocal()

    try:

        user = db.query(User).filter(
            User.email == current_user
        ).first()

        if user is None:
            return {
                "message": "User not found"
            }

        employee = db.query(Employee).filter(
            Employee.email == user.email
        ).first()

        if employee is None:
            return {
                "message": "Employee not found"
            }

        attendance_count = db.query(Attendance).filter(
            Attendance.employee_id == employee.id
        ).count()

        leave_count = db.query(LeaveRequest).filter(
            LeaveRequest.employee_id == employee.id
        ).count()

        payroll_count = db.query(Payroll).filter(
            Payroll.employee_id == employee.id
        ).count()

        performance_count = db.query(Performance).filter(
            Performance.employee_id == employee.id
        ).count()

        today = db.query(Attendance).filter(
            Attendance.employee_id == employee.id,
            Attendance.attendance_date == date.today()
        ).first()

        return {

            "employee": {

                "employee_id": employee.employee_id,

                "full_name": employee.full_name,

                "designation": employee.designation,

                "department": employee.department.department_name,

                "superior": {
                    "id": employee.superior.id if employee.superior else None,
                    "name": employee.superior.full_name if employee.superior else None,
                    "email": employee.superior.email if employee.superior else None,
                }

            },

            "attendance_count": attendance_count,

            "leave_count": leave_count,

            "payroll_count": payroll_count,

            "performance_count": performance_count,

            "today_attendance": {

                "status": today.status if today else "Not Checked In",

                "check_in": str(today.check_in) if today else "-",

                "check_out": str(today.check_out) if today else "-"

            }

        }

    finally:

        db.close()
def get_employee_profile(email):

    db = SessionLocal()

    try:

        employee = db.query(Employee).filter(
            Employee.email == email
        ).first()

        if employee is None:
            return None

        return {

            "employee_id": employee.employee_id,

            "full_name": employee.full_name,

            "email": employee.email,

            "department": employee.department.department_name
            if employee.department else "",

            "designation": employee.designation,

            "salary": employee.salary,

            "phone": getattr(employee, "phone", "")

        }

    finally:

        db.close()