import asyncio
import os
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import Base, engine, SessionLocal
import backend.models
from backend.services.hierarchy_performance_service import auto_finalize_previous_month
from backend.routers import (
    home_router,
    employee_documents,
    employee_details,
    performance,
    hierarchy_performance,
    me,
    auth,
    users,
    employees,
    departments,
    attendance,
    dashboard,
    leave,
    payroll,
    reports,
    profile,
    onboarding,
    offboarding,
    employee_profile,
    change_password,
    profile_photo,
    ai_router,
    resume_router,
    hr_ai_router,
    sentiment_router,
)
from backend.routers.profile_router import router as profile_router

Base.metadata.create_all(bind=engine)


async def _performance_scheduler():
    while True:
        try:
            db = SessionLocal()
            try:
                auto_finalize_previous_month(db)
            finally:
                db.close()
        except Exception:
            # Scheduler failures must not terminate the API process.
            pass
        await asyncio.sleep(3600)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_performance_scheduler())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


app = FastAPI(
    title="Employee Management Portal API",
    description="Professional HRMS Backend using FastAPI",
    version="2.0.0",
    lifespan=lifespan,
)

os.makedirs("backend/uploads/profile_photos", exist_ok=True)
os.makedirs("backend/uploads/documents", exist_ok=True)
os.makedirs("backend/uploads/resumes", exist_ok=True)
os.makedirs("backend/uploads/policies", exist_ok=True)

app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")
app.mount("/backend/uploads", StaticFiles(directory="backend/uploads"), name="backend-uploads")

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(home_router.router)
app.include_router(employee_details.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(employees.router)
app.include_router(departments.router)
app.include_router(attendance.router)
app.include_router(dashboard.router)
app.include_router(leave.router)
app.include_router(payroll.router)
app.include_router(reports.router)
app.include_router(profile.router)
app.include_router(me.router)
app.include_router(performance.router)
app.include_router(hierarchy_performance.router)
app.include_router(onboarding.router)
app.include_router(offboarding.router)
app.include_router(employee_profile.router)
app.include_router(change_password.router)
app.include_router(profile_router)
app.include_router(employee_documents.router)
app.include_router(ai_router.router)
app.include_router(profile_photo.router)
app.include_router(resume_router.router)
app.include_router(hr_ai_router.router)
app.include_router(sentiment_router.router)


@app.get("/")
def home():
    return {"message": "Employee Management Portal API is Running Successfully 🚀"}
