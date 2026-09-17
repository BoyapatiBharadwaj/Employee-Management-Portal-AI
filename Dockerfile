FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY .env.example ./.env.example

RUN mkdir -p /app/backend/uploads/profile_photos \
    /app/backend/uploads/documents \
    /app/backend/uploads/resumes \
    /app/backend/uploads/policies \
    /app/backend/rag/chroma_db

EXPOSE 8000

CMD ["sh", "-c", "python -m backend.migrations.upgrade && python -m backend.seed && uvicorn backend.app:app --host 0.0.0.0 --port 8000"]
