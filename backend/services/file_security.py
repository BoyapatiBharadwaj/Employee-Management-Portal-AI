import os
import re
import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile
from backend.config import settings


def safe_extension(filename: str) -> str:
    return Path(filename or "").suffix.lower()


def generate_safe_filename(original: str) -> str:
    name = Path(original or "file").name
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(name).stem)[:80] or "file"
    return f"{uuid.uuid4().hex}_{stem}{safe_extension(name)}"


async def save_upload(file: UploadFile, destination_dir: str, allowed_extensions: set[str]) -> tuple[str, str]:
    extension = safe_extension(file.filename)
    if extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {extension or 'unknown'}")
    data = await file.read()
    if len(data) > settings.UPLOAD_MAX_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.UPLOAD_MAX_MB} MB upload limit")
    safe_name = generate_safe_filename(file.filename or "file")
    os.makedirs(destination_dir, exist_ok=True)
    path = os.path.join(destination_dir, safe_name)
    with open(path, "wb") as handle:
        handle.write(data)
    return path, safe_name
