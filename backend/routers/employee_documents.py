from fastapi import APIRouter, Depends, UploadFile, File, Form
from backend.auth import get_current_user, verify_admin
from backend.models import User
from backend.services import employee_document_service

router = APIRouter(tags=["Employee Documents"])


@router.post("/employee/documents/upload")
async def upload_document(document_type: str = Form(...), file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    return employee_document_service.upload_document(current_user.email, document_type, file)


@router.get("/employee/documents")
def get_my_documents(current_user: User = Depends(get_current_user)):
    return employee_document_service.get_my_documents(current_user.email)


@router.get("/admin/documents")
def all_documents(admin: User = Depends(verify_admin)):
    return employee_document_service.get_all_documents()


@router.put("/admin/documents/{document_id}/approve")
def approve(document_id: int, admin: User = Depends(verify_admin)):
    return employee_document_service.approve_document(document_id)


@router.put("/admin/documents/{document_id}/reject")
def reject(document_id: int, admin: User = Depends(verify_admin)):
    return employee_document_service.reject_document(document_id)


@router.delete("/employee/documents/{document_id}")
def delete_document(document_id: int, current_user: User = Depends(get_current_user)):
    return employee_document_service.delete_document(document_id, current_user.email)
