import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from backend.auth import verify_admin
from backend.models import User
from backend.ai.resume_ai import resume_ai
from backend.ai.semantic_search import semantic_search
from backend.services.file_security import save_upload

router = APIRouter(prefix="/resume", tags=["Resume AI"])
class SearchRequest(BaseModel):
    query: str
UPLOAD_FOLDER = "backend/resume_storage/resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/analyze")
async def analyze_resume(file: UploadFile = File(...), admin: User = Depends(verify_admin)):
    file_path, safe_name = await save_upload(file, UPLOAD_FOLDER, {".pdf", ".docx"})
    analysis = resume_ai.analyze_resume(file_path)
    return {"filename": file.filename, "stored_filename": safe_name, "analysis": analysis}


@router.post("/search")
def search_resume(request: SearchRequest, admin: User = Depends(verify_admin)):
    return {"results": semantic_search.search(query=request.query, top_k=5)}
