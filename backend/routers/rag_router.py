import os
from fastapi import APIRouter, UploadFile, File, Depends
from pydantic import BaseModel
from backend.auth import verify_admin
from backend.models import User
from backend.rag.rag_service import rag_service
from backend.services.file_security import save_upload

router = APIRouter(prefix="/rag", tags=["RAG HR Policy"])
UPLOAD_FOLDER = "backend/rag/policies"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class ChatRequest(BaseModel):
    question: str


@router.post("/upload-policy")
async def upload_policy(file: UploadFile = File(...), admin: User = Depends(verify_admin)):
    file_path, safe_name = await save_upload(file, UPLOAD_FOLDER, {".pdf"})
    chunks = rag_service.ingest_pdf(file_path)
    return {"message": "Policy uploaded successfully.", "chunks": chunks, "filename": safe_name}


@router.post("/chat")
def chat(request: ChatRequest, admin: User = Depends(verify_admin)):
    return {"answer": rag_service.ask(request.question)}
