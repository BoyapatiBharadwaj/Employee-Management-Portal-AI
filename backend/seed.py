from datetime import date

from backend.database import SessionLocal
from backend.models import User, Employee, Department, EmployeeSuperiorHistory
from backend.auth import hash_password


def _get_or_create_user(db, username, email, password, role):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(username=username, email=email, password=hash_password(password), role=role)
        db.add(user)
        db.flush()
    return user


def _get_or_create_employee(db, employee_id, full_name, email, department_id, designation, salary):
    employee = db.query(Employee).filter(Employee.email == email).first()
    if not employee:
        employee = Employee(
            employee_id=employee_id,
            full_name=full_name,
            email=email,
            department_id=department_id,
            designation=designation,
            salary=salary,
        )
        db.add(employee)
        db.flush()
    return employee


def _ensure_history(db, employee, superior_id):
    if employee.superior_id is not None:
        return
    employee.superior_id = superior_id
    active = db.query(EmployeeSuperiorHistory).filter(
        EmployeeSuperiorHistory.employee_id == employee.id,
        EmployeeSuperiorHistory.effective_to.is_(None),
    ).first()
    if not active:
        db.add(EmployeeSuperiorHistory(
            employee_id=employee.id,
            superior_id=superior_id,
            effective_from=date.today(),
        ))


def seed_database():
    db = SessionLocal()
    try:
        administration = db.query(Department).filter(Department.department_name == "Administration").first()
        if not administration:
            administration = Department(department_name="Administration", description="System Administration")
            db.add(administration)
            db.flush()

        engineering = db.query(Department).filter(Department.department_name == "Engineering").first()
        if not engineering:
            engineering = Department(department_name="Engineering", description="Engineering and Technology")
            db.add(engineering)
            db.flush()

        _get_or_create_user(db, "admin", "admin@example.com", "admin123", "Admin")
        ceo_user = _get_or_create_user(db, "ceo", "ceo@example.com", "ceo12345", "CEO")
        manager_user = _get_or_create_user(db, "manager", "manager@example.com", "manager123", "Superior")
        _get_or_create_user(db, "shyam", "shyam@gmail.com", "123456", "Employee")

        admin_employee = _get_or_create_employee(db, "EMP001", "Administrator", "admin@example.com", administration.id, "HR Administrator", 100000)
        ceo_employee = _get_or_create_employee(db, "EMP003", "Chief Executive Officer", "ceo@example.com", administration.id, "CEO", 250000)
        manager_employee = _get_or_create_employee(db, "EMP004", "Reporting Manager", "manager@example.com", engineering.id, "Engineering Manager", 150000)
        employee = _get_or_create_employee(db, "EMP002", "Shyam", "shyam@gmail.com", engineering.id, "Employee", 50000)

        _ensure_history(db, manager_employee, ceo_employee.id)
        _ensure_history(db, employee, manager_employee.id)
        _ensure_history(db, admin_employee, ceo_employee.id)

        db.commit()
        print("Database seeded successfully.")
        print("Admin: admin@example.com / admin123")
        print("CEO: ceo@example.com / ceo12345")
        print("Superior: manager@example.com / manager123")
        print("Employee: shyam@gmail.com / 123456")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
