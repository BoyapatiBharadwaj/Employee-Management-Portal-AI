from fastapi import APIRouter, Depends, HTTPException
from backend.schemas import OnboardingCreate
from backend.auth import verify_admin, get_current_user
from backend.models import User, Employee
from backend.database import SessionLocal
from backend.services import onboarding_service

router = APIRouter(tags=["Onboarding"])

@router.post("/onboarding")
def create_onboarding(onboarding: OnboardingCreate, admin: User = Depends(verify_admin)):
    return onboarding_service.create_onboarding(onboarding)

@router.get("/onboarding")
def get_onboarding(admin: User = Depends(verify_admin)):
    return onboarding_service.get_onboarding()

@router.get("/onboarding/{employee_id}")
def get_employee_onboarding(employee_id: int, current_user: User = Depends(get_current_user)):
    if current_user.role == "Admin":
        return onboarding_service.get_employee_onboarding(employee_id)
    db = SessionLocal()
    try:
        emp = db.query(Employee).filter(Employee.email.ilike(current_user.email)).first()
        if not emp or emp.id != employee_id:
            raise HTTPException(status_code=403, detail="You can only view your own onboarding")
        return onboarding_service.get_employee_onboarding(employee_id)
    finally:
        db.close()

@router.delete("/onboarding/{onboarding_id}")
def delete_onboarding(onboarding_id: int, admin: User = Depends(verify_admin)):
    return onboarding_service.delete_onboarding(onboarding_id)
