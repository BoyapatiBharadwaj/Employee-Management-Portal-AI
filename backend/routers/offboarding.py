from fastapi import APIRouter, Depends, HTTPException
from backend.schemas import OffboardingCreate
from backend.auth import verify_admin, get_current_user
from backend.models import User, Employee
from backend.database import SessionLocal
from backend.services import offboarding_service
from backend.services.retention_service import retention_blocks_deletion

router = APIRouter(tags=["Offboarding"])

@router.post("/offboarding")
def create_offboarding(offboarding: OffboardingCreate, admin: User = Depends(verify_admin)):
    return offboarding_service.create_offboarding(offboarding)

@router.get("/offboarding")
def get_offboarding(admin: User = Depends(verify_admin)):
    return offboarding_service.get_offboarding()

@router.get("/offboarding/{employee_id}")
def get_employee_offboarding(employee_id: int, current_user: User = Depends(get_current_user)):
    if current_user.role == "Admin":
        return offboarding_service.get_employee_offboarding(employee_id)
    db = SessionLocal()
    try:
        emp = db.query(Employee).filter(Employee.email.ilike(current_user.email)).first()
        if not emp or emp.id != employee_id:
            raise HTTPException(status_code=403, detail="You can only view your own offboarding record")
        return offboarding_service.get_employee_offboarding(employee_id)
    finally:
        db.close()

@router.delete("/offboarding/{offboarding_id}")
def delete_offboarding(offboarding_id: int, admin: User = Depends(verify_admin)):
    db = SessionLocal()
    try:
        from backend.models import Offboarding
        record = db.query(Offboarding).filter(Offboarding.id == offboarding_id).first()
        if record and retention_blocks_deletion(db, record.employee_id):
            raise HTTPException(status_code=409, detail="Employment/offboarding data is protected by the 7-year retention policy")
    finally:
        db.close()
    return offboarding_service.delete_offboarding(offboarding_id)
