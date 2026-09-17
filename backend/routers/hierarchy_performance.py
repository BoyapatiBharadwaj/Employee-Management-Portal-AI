from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.auth import get_current_user, verify_admin, verify_superior
from backend.database import SessionLocal
from backend.models import User, EmployeeSuperiorHistory
from backend.schemas.monthly_performance import (
    SuperiorAssignmentCreate,
    MonthlyEvaluationCreate,
    MonthlyPerformanceCorrectionCreate,
)
from backend.services.hierarchy_performance_service import (
    assign_superior,
    get_superior,
    get_team,
    upsert_monthly_evaluation,
    correct_finalized_evaluation,
    finalize_month,
    get_my_history,
    get_team_performance,
    get_insights,
    get_audit_logs,
    get_notifications,
    mark_notification_read,
    mark_all_notifications_read,
    get_retention_status,
)

router = APIRouter(tags=["Hierarchy & Monthly Performance"])


def _call(func, *args, **kwargs):
    db = SessionLocal()
    try:
        return func(db, *args, **kwargs)
    except (ValueError, PermissionError) as exc:
        db.rollback()
        status = 403 if isinstance(exc, PermissionError) else 400
        raise HTTPException(status_code=status, detail=str(exc))
    finally:
        db.close()


@router.get("/hierarchy/my-superior")
def current_superior(current_user: User = Depends(get_current_user)):
    return _call(get_superior, current_user)


@router.get("/hierarchy/team")
def my_team(
    performance_month: date | None = Query(default=None),
    current_user: User = Depends(verify_superior),
):
    return _call(get_team, current_user, performance_month)


@router.post("/hierarchy/{employee_id}/superior")
def set_superior(employee_id: int, payload: SuperiorAssignmentCreate, admin: User = Depends(verify_admin)):
    return _call(assign_superior, admin, employee_id, payload.superior_id, payload.effective_from)


@router.get("/hierarchy/history/{employee_id}")
def hierarchy_history(employee_id: int, admin: User = Depends(verify_admin)):
    db = SessionLocal()
    try:
        rows = db.query(EmployeeSuperiorHistory).filter(
            EmployeeSuperiorHistory.employee_id == employee_id
        ).order_by(EmployeeSuperiorHistory.effective_from.desc()).all()
        return [{
            "id": row.id,
            "employee_id": row.employee_id,
            "superior_id": row.superior_id,
            "superior_name": row.superior.full_name if row.superior else None,
            "effective_from": row.effective_from,
            "effective_to": row.effective_to,
            "changed_at": row.changed_at,
            "changed_by": row.changed_by.username if row.changed_by else None,
        } for row in rows]
    finally:
        db.close()


@router.post("/performance/monthly/evaluate")
def evaluate_monthly(payload: MonthlyEvaluationCreate, current_user: User = Depends(verify_superior)):
    return _call(upsert_monthly_evaluation, current_user, payload.employee_id, payload.performance_month, payload.rating, payload.feedback)


@router.post("/performance/monthly/correct")
def correct_monthly(payload: MonthlyPerformanceCorrectionCreate, admin: User = Depends(verify_admin)):
    return _call(correct_finalized_evaluation, admin, payload.record_id, payload.rating, payload.feedback, payload.reason)


@router.get("/performance/monthly/me")
def my_monthly_performance(current_user: User = Depends(get_current_user)):
    return _call(get_my_history, current_user)


@router.get("/performance/monthly/team")
def team_monthly_performance(
    performance_month: date | None = Query(default=None),
    current_user: User = Depends(verify_superior),
):
    return _call(get_team_performance, current_user, performance_month)


@router.get("/performance/insights")
def performance_insights(
    performance_month: date | None = Query(default=None),
    department_id: int | None = Query(default=None),
    superior_id: int | None = Query(default=None),
    employee_id: int | None = Query(default=None),
    rank: int | None = Query(default=None),
    ranking_scope: str = Query(default="overall", pattern="^(overall|department|superior)$"),
    sort_by: str = Query(default="rank", pattern="^(rank|overall_score|employee_name|department|superior_name)$"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
    admin: User = Depends(verify_admin),
):
    return _call(get_insights, admin, performance_month, department_id, superior_id, employee_id, rank, ranking_scope, sort_by, sort_order)


@router.post("/performance/monthly/finalize")
def finalize_monthly(performance_month: date, admin: User = Depends(verify_admin)):
    return _call(finalize_month, admin, performance_month)


@router.get("/audit-logs")
def audit_logs(admin: User = Depends(verify_admin)):
    db = SessionLocal()
    try:
        return get_audit_logs(db)
    finally:
        db.close()


@router.get("/notifications/me")
def my_notifications(
    unread_only: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
):
    db = SessionLocal()
    try:
        return get_notifications(db, current_user, unread_only)
    finally:
        db.close()


@router.put("/notifications/{notification_id}/read")
def read_notification(notification_id: int, current_user: User = Depends(get_current_user)):
    return _call(mark_notification_read, current_user, notification_id)


@router.put("/notifications/read-all")
def read_all_notifications(current_user: User = Depends(get_current_user)):
    return _call(mark_all_notifications_read, current_user)


@router.get("/retention/status")
def retention_status(
    employee_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
):
    return _call(get_retention_status, current_user, employee_id)
