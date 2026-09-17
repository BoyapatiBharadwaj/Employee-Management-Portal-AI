import os
import shutil

from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models.employee import Employee
from backend.models.employee_document import EmployeeDocument

UPLOAD_FOLDER = "backend/uploads/employee_documents"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def upload_document(
    current_user: str,
    document_type: str,
    file: UploadFile
):

    db: Session = SessionLocal()

    try:

        employee = db.query(Employee).filter(
            Employee.email == current_user
        ).first()

        if employee is None:

            return {
                "message": "Employee not found"
            }

        filename = f"{employee.employee_id}_{document_type}_{file.filename}"

        filepath = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        with open(filepath, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        document = EmployeeDocument(

            employee_id=employee.id,

            document_type=document_type,

            document_name=file.filename,

            file_path=f"/uploads/employee_documents/{filename}",

            status="Pending"

        )

        db.add(document)

        db.commit()

        db.refresh(document)

        return {

            "message": "Document uploaded successfully",

            "document": {

                "id": document.id,

                "document_type": document.document_type,

                "document_name": document.document_name,

                "status": document.status

            }

        }

    finally:

        db.close()
def get_my_documents(current_user: str):

    db: Session = SessionLocal()

    try:

        employee = db.query(Employee).filter(
            Employee.email == current_user
        ).first()

        if employee is None:

            return []

        documents = db.query(EmployeeDocument).filter(
            EmployeeDocument.employee_id == employee.id
        ).all()

        return documents

    finally:

        db.close()

# ==========================================
# Admin - All Documents
# ==========================================

def get_all_documents():

    db: Session = SessionLocal()

    try:

        documents = db.query(EmployeeDocument).all()

        return documents

    finally:

        db.close()


# ==========================================
# Approve Document
# ==========================================

def approve_document(document_id: int):

    db: Session = SessionLocal()

    try:

        document = db.query(EmployeeDocument).filter(
            EmployeeDocument.id == document_id
        ).first()

        if not document:

            return {
                "message": "Document not found."
            }

        document.status = "Approved"

        db.commit()

        return {
            "message": "Document approved successfully."
        }

    finally:

        db.close()


# ==========================================
# Reject Document
# ==========================================

def reject_document(document_id: int):

    db: Session = SessionLocal()

    try:

        document = db.query(EmployeeDocument).filter(
            EmployeeDocument.id == document_id
        ).first()

        if not document:

            return {
                "message": "Document not found."
            }

        document.status = "Rejected"

        db.commit()

        return {
            "message": "Document rejected successfully."
        }

    finally:

        db.close()

# ==========================================
# Delete Document
# ==========================================

def delete_document(document_id: int, current_user: str):

    db: Session = SessionLocal()

    try:

        document = db.query(EmployeeDocument).filter(
            EmployeeDocument.id == document_id
        ).first()

        if document is None:
            return {"message": "Document not found."}

        employee = db.query(Employee).filter(Employee.email == current_user).first()
        if employee is None or document.employee_id != employee.id:
            return {"message": "You can only delete your own document."}

        if document.status != "Pending":

            return {
                "message": "Approved or Rejected documents cannot be deleted."
            }

        real_path = "backend" + document.file_path

        if os.path.exists(real_path):

            os.remove(real_path)

        db.delete(document)

        db.commit()

        return {

            "message": "Document deleted successfully."

        }

    finally:

        db.close()