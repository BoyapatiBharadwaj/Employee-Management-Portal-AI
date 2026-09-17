from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.auth import verify_admin
from backend.models import User
from backend.ai.sentiment_ai import sentiment_ai

router = APIRouter(prefix="/sentiment", tags=["Sentiment Analysis"])


class Feedback(BaseModel):
    feedback: str


@router.post("/analyze")
def analyze(data: Feedback, admin: User = Depends(verify_admin)):
    return {"result": sentiment_ai.analyze(data.feedback)}
