from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.database import SessionLocal
from backend.models import User, Employee
from backend.auth import (
    hash_password,
    verify_password,
    create_access_token
)
from backend.schemas import UserCreate

router = APIRouter(
    tags=["Authentication"]
)


# ==========================
# Register
# ==========================
@router.post("/register")
def register(user: UserCreate):
    db: Session = SessionLocal()

    try:
        new_user = User(
            username=user.username,
            email=user.email,
            password=hash_password(user.password),
            role=user.role
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User registered successfully",
            "user_id": new_user.id
        }

    except Exception as e:
        db.rollback()
        return {"error": str(e)}

    finally:
        db.close()


# ==========================
# Login
# ==========================
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db: Session = SessionLocal()
    try:
        email = form_data.username.strip().lower()
        db_user = db.query(User).filter(User.email.ilike(email)).first()

        if db_user is None or not verify_password(form_data.password, db_user.password):
            return {"message": "Invalid email or password"}

        emp = db.query(Employee).filter(Employee.email.ilike(db_user.email)).first()
        token = create_access_token({"sub": db_user.email})

        return {
            "access_token": token,
            "token_type": "bearer",
            "role": db_user.role,
            "employee_id": emp.id if emp else None,
            "user": {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email,
                "role": db_user.role
            }
        }
    finally:
        db.close()
