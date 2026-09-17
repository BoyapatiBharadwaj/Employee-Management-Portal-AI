# Implementation Notes — Groq, Docker, Employee Hierarchy & Monthly Performance

## LLM Provider
- Replaced the local Ollama HTTP integration with the Groq Python SDK.
- Default model: `openai/gpt-oss-20b`.
- Configure `GROQ_API_KEY` and override `GROQ_MODEL` in `.env` when needed.
- The key is never committed to the project.

## Docker
- Added environment-driven PostgreSQL, FastAPI, Groq, JWT, CORS and calculation settings.
- Backend runs a database upgrade before FastAPI starts.
- Frontend accepts `VITE_API_URL` as a Docker build argument.
- PostgreSQL, upload storage and Chroma storage use named Docker volumes.

## Client Requirements Implemented
- Admin-controlled active Superior assignment with historical relationship records.
- Current Superior visibility in employee dashboard/monthly-performance view.
- Direct-report team view for Superior/CEO/Admin roles.
- Monthly evaluation with a 1–100 rating and feedback.
- Evaluation window enforcement: 25th through month-end.
- Pending Review records and in-app notifications/reminders.
- Performance calculation: Superior 60%, Attendance 25%, Leave 15%.
- 1–100 normalized component scores and competition ranking.
- Previous-month Performance Insights for Admin.
- Department/Superior/employee/month/rank API filters.
- Finalization and read-only behavior for Employee/Superior, with Admin correction capability.
- Audit log persistence for hierarchy changes, evaluations and month processing.
- Hourly backend scheduler to finalize the previous month, create pending records and generate reminders.

## Important Configuration Boundary
Attendance and leave normalization parameters are configurable through environment variables while preserving the approved 60/25/15 weighting. The supplied requirements document explicitly allows implementation-level normalization parameters to be configured as long as the approved weighting is preserved.


## Docker startup fixes (2026-09-17)
- Fixed `backend/app.py` so the AI router is included as `ai_router.router`; the previous code passed the Python module to FastAPI.
- Made `backend/seed.py` idempotent and ensured the Administration department exists before creating seeded records.
- Updated Docker startup to run the idempotent seed after database migration and before Uvicorn.
