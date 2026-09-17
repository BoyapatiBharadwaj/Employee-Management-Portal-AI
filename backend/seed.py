from backend.database import SessionLocal
from backend.models import User, Employee, Department
from backend.auth import hash_password


def seed_database():
    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # Department
        # ---------------------------------------------------------
        department = (
            db.query(Department)
            .filter(Department.department_name == "Administration")
            .first()
        )

        if not department:
            department = Department(
                department_name="Administration",
                description="System Administration",
            )
            db.add(department)
            db.flush()

        # ---------------------------------------------------------
        # Admin user
        # ---------------------------------------------------------
        admin_user = (
            db.query(User)
            .filter(User.email == "admin@example.com")
            .first()
        )

        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password=hash_password("admin123"),
                role="Admin",
            )
            db.add(admin_user)

        # ---------------------------------------------------------
        # Admin employee profile
        # ---------------------------------------------------------
        admin_employee = (
            db.query(Employee)
            .filter(Employee.email == "admin@example.com")
            .first()
        )

        if not admin_employee:
            admin_employee = Employee(
                employee_id="EMP001",
                full_name="Administrator",
                email="admin@example.com",
                department_id=department.id,
                designation="Administrator",
                salary=100000,
            )
            db.add(admin_employee)

        # ---------------------------------------------------------
        # Demo employee user
        # ---------------------------------------------------------
        employee_user = (
            db.query(User)
            .filter(User.email == "shyam@gmail.com")
            .first()
        )

        if not employee_user:
            employee_user = User(
                username="shyam",
                email="shyam@gmail.com",
                password=hash_password("123456"),
                role="Employee",
            )
            db.add(employee_user)

        # ---------------------------------------------------------
        # Demo employee profile
        # ---------------------------------------------------------
        employee = (
            db.query(Employee)
            .filter(Employee.email == "shyam@gmail.com")
            .first()
        )

        if not employee:
            employee = Employee(
                employee_id="EMP002",
                full_name="Shyam",
                email="shyam@gmail.com",
                department_id=department.id,
                designation="Employee",
                salary=50000,
            )
            db.add(employee)

        db.commit()

        print("Database seeded successfully.")
        print("Admin: admin@example.com / admin123")
        print("Employee: shyam@gmail.com / 123456")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
