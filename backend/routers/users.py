from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import User
from backend.auth import verify_admin, hash_password
from backend.models import Employee
from backend.services.retention_service import retention_blocks_deletion

router = APIRouter(tags=["Users"])


class UserAdminUpdate(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    email: str
    password: str = Field(min_length=8, max_length=255)
    role: str = Field(pattern="^(Admin|Superior|CEO|Employee)$")


@router.get("/users")
def get_users(admin: User = Depends(verify_admin)):
    db: Session = SessionLocal()
    try:
        return db.query(User).order_by(User.id).all()
    finally:
        db.close()


@router.get("/users/{user_id}")
def get_user(user_id: int, admin: User = Depends(verify_admin)):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"message": "User not found"}
        return user
    finally:
        db.close()


@router.put("/users/{user_id}")
def update_user(user_id: int, user: UserAdminUpdate, admin: User = Depends(verify_admin)):
    db: Session = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.id == user_id).first()
        if not existing_user:
            return {"message": "User not found"}
        existing_user.username = user.username.strip()
        existing_user.email = user.email.strip().lower()
        existing_user.password = hash_password(user.password)
        existing_user.role = user.role
        db.commit()
        db.refresh(existing_user)
        return {"message": "User updated successfully", "user": existing_user}
    finally:
        db.close()


@router.delete("/users/{user_id}")
def delete_user(user_id: int, admin: User = Depends(verify_admin)):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"message": "User not found"}
        if user.id == admin.id:
            return {"message": "An Admin cannot delete their own account"}
        employee = db.query(Employee).filter(Employee.email.ilike(user.email)).first()
        if employee and retention_blocks_deletion(db, employee.id):
            return {"message": "User account is protected while HR records are within the employment + 7-year retention period"}
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    finally:
        db.close()
