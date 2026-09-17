from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from backend.config import settings
from backend.models import (
    Employee,
    EmployeeSuperiorHistory,
    MonthlyPerformance,
    User,
    Attendance,
    LeaveRequest,
    AuditLog,
    Notification,
    Offboarding,
)
from backend.services.retention_service import retention_summary


def business_today() -> date:
    return datetime.now(ZoneInfo(settings.BUSINESS_TIMEZONE)).date()


def business_now() -> datetime:
    return datetime.now(ZoneInfo(settings.BUSINESS_TIMEZONE))


def month_start(value: date) -> date:
    return date(value.year, value.month, 1)


def month_end(value: date) -> date:
    return date(value.year, value.month, monthrange(value.year, value.month)[1])


def add_months(value: date, count: int) -> date:
    month = value.month - 1 + count
    year = value.year + month // 12
    month = month % 12 + 1
    return date(year, month, 1)


def evaluation_window_open(performance_month: date, today: Optional[date] = None) -> bool:
    today = today or business_today()
    start = date(performance_month.year, performance_month.month, 25)
    end = month_end(performance_month)
    return start <= today <= end


def previous_month(value: Optional[date] = None) -> date:
    value = value or business_today()
    return add_months(month_start(value), -1)


def _employee_for_user(db: Session, user: User) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.email.ilike(user.email)).first()


def _user_for_employee(db: Session, employee: Employee) -> Optional[User]:
    return db.query(User).filter(User.email.ilike(employee.email)).first()


def _audit(db: Session, actor: Optional[User], action: str, entity_type: str, entity_id: Optional[int], details: str):
    db.add(AuditLog(
        actor_user_id=actor.id if actor else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    ))


def _ensure_no_cycle(db: Session, employee_id: int, superior_id: Optional[int]):
    if superior_id is None:
        return
    if employee_id == superior_id:
        raise ValueError("An employee cannot be their own Superior")

    seen = set()
    current = db.query(Employee).filter(Employee.id == superior_id).first()
    while current:
        if current.id in seen:
            raise ValueError("The existing hierarchy contains a cycle")
        seen.add(current.id)
        if current.id == employee_id:
            raise ValueError("This assignment would create a reporting cycle")
        current = current.superior


def _validate_superior_role(db: Session, employee: Employee, superior: Optional[Employee]):
    target_user = _user_for_employee(db, employee)
    if target_user and target_user.role == "CEO" and superior is not None:
        raise ValueError("CEO is the top-level exception and cannot have a Superior")
    if superior is None:
        return
    superior_user = _user_for_employee(db, superior)
    if not superior_user or superior_user.role not in {"Superior", "CEO"}:
        raise ValueError("The assigned reporting manager must have Superior or CEO role")


def assign_superior(db: Session, actor: User, employee_id: int, superior_id: Optional[int], effective_from: date):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise ValueError("Employee not found")

    today = business_today()
    if effective_from != today:
        raise ValueError("Superior changes must take effect on the organization's current business date")

    superior = None
    if superior_id is not None:
        superior = db.query(Employee).filter(Employee.id == superior_id).first()
        if not superior:
            raise ValueError("Superior not found")
        _ensure_no_cycle(db, employee_id, superior_id)

    _validate_superior_role(db, employee, superior)

    previous = employee.superior_id
    if previous == superior_id:
        return employee

    latest_history = (
        db.query(EmployeeSuperiorHistory)
        .filter(EmployeeSuperiorHistory.employee_id == employee.id)
        .order_by(EmployeeSuperiorHistory.effective_from.desc())
        .first()
    )
    if latest_history and effective_from <= latest_history.effective_from:
        raise ValueError("Historical Superior changes must move forward in time")

    active_history = (
        db.query(EmployeeSuperiorHistory)
        .filter(
            EmployeeSuperiorHistory.employee_id == employee.id,
            EmployeeSuperiorHistory.effective_to.is_(None),
        )
        .order_by(EmployeeSuperiorHistory.effective_from.desc())
        .first()
    )
    if active_history:
        if effective_from <= active_history.effective_from:
            raise ValueError("Effective date must be after the current active assignment start date")
        active_history.effective_to = effective_from - timedelta(days=1)

    employee.superior_id = superior_id
    db.flush()

    db.add(EmployeeSuperiorHistory(
        employee_id=employee.id,
        superior_id=superior_id,
        effective_from=effective_from,
        changed_by_user_id=actor.id,
    ))
    _audit(
        db, actor, "SUPERIOR_CHANGED", "Employee", employee.id,
        f"Superior changed from {previous} to {superior_id}; effective_from={effective_from.isoformat()}",
    )
    db.commit()
    db.refresh(employee)
    return employee


def get_superior(db: Session, user: User):
    employee = _employee_for_user(db, user)
    if not employee:
        raise ValueError("Employee profile not found")
    superior = employee.superior
    return {
        "employee_id": employee.id,
        "employee_name": employee.full_name,
        "superior_id": superior.id if superior else None,
        "superior_name": superior.full_name if superior else None,
        "superior_email": superior.email if superior else None,
        "role": "CEO" if user.role == "CEO" else ("Assigned Superior" if superior else "No Superior Assigned"),
    }


def get_team(db: Session, user: User, performance_month: Optional[date] = None):
    employee = _employee_for_user(db, user)
    if not employee:
        raise ValueError("Employee profile not found")
    target = month_start(performance_month or business_today())
    rows = db.query(Employee).options(joinedload(Employee.department)).filter(
        Employee.superior_id == employee.id
    ).order_by(Employee.full_name).all()
    records = {
        row.employee_id: row for row in db.query(MonthlyPerformance).filter(
            MonthlyPerformance.performance_month == target,
            MonthlyPerformance.employee_id.in_([e.id for e in rows] or [-1]),
        ).all()
    }
    return [{
        "id": emp.id,
        "employee_id": emp.employee_id,
        "full_name": emp.full_name,
        "email": emp.email,
        "department_id": emp.department_id,
        "department": emp.department.department_name if emp.department else None,
        "designation": emp.designation,
        "superior_id": emp.superior_id,
        "performance_month": target,
        "evaluation_status": records[emp.id].status if emp.id in records else "Pending Review",
        "superior_rating": records[emp.id].superior_rating if emp.id in records else None,
        "attendance_score": records[emp.id].attendance_score if emp.id in records else None,
        "leave_score": records[emp.id].leave_score if emp.id in records else None,
        "overall_score": records[emp.id].overall_score if emp.id in records else None,
        "rank": records[emp.id].rank if emp.id in records else None,
    } for emp in rows]


def _working_days(start: date, end: date) -> int:
    count = 0
    cursor = start
    while cursor <= end:
        if cursor.weekday() < 5:
            count += 1
        cursor += timedelta(days=1)
    return count


def _attendance_inputs(db: Session, employee: Employee, performance_month: date):
    start = month_start(performance_month)
    end = month_end(performance_month)
    rows = db.query(Attendance).filter(
        Attendance.employee_id == employee.id,
        Attendance.attendance_date.between(start, end),
    ).all()
    present = sum(1 for row in rows if str(row.status).lower() in {"present", "late", "half day", "half-day"})
    absent = sum(1 for row in rows if str(row.status).lower() == "absent")
    late_days = sum(1 for row in rows if (row.late_minutes or 0) > 0 or str(row.status).lower() == "late")
    late_minutes = sum(int(row.late_minutes or 0) for row in rows)
    scheduled_start = max(start, employee.joining_date) if employee.joining_date else start
    scheduled = _working_days(scheduled_start, end) if scheduled_start <= end else 0
    return {
        "present_days": present,
        "absent_days": absent,
        "late_days": late_days,
        "late_minutes": late_minutes,
        "scheduled_days": scheduled,
        "record_count": len(rows),
    }


def _attendance_score(inputs: dict) -> float:
    denominator = inputs["scheduled_days"] or (inputs["present_days"] + inputs["absent_days"])
    if denominator <= 0:
        return 100.0
    present = min(inputs["present_days"], denominator)
    absent = max(inputs["absent_days"], denominator - present) if inputs["record_count"] else 0
    base = (present / denominator) * 100
    score = base - (inputs["late_days"] * settings.ATTENDANCE_LATE_PENALTY) - (absent * settings.ATTENDANCE_ABSENCE_PENALTY)
    return round(max(0.0, min(100.0, score)), 2)


def _leave_inputs(db: Session, employee_id: int, performance_month: date, scheduled_days: int):
    start = month_start(performance_month)
    end = month_end(performance_month)
    rows = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.start_date <= end,
        LeaveRequest.end_date >= start,
    ).all()
    approved_days = rejected_days = unplanned_days = 0
    for row in rows:
        overlap_start = max(row.start_date, start)
        overlap_end = min(row.end_date, end)
        days = max(0, (overlap_end - overlap_start).days + 1)
        status = (row.status or "").lower()
        leave_type = (row.leave_type or "").lower()
        if status == "approved":
            approved_days += days
        elif status == "rejected":
            rejected_days += 1
        if "emergency" in leave_type or "unplanned" in leave_type:
            unplanned_days += days
    leave_percentage = round((approved_days / scheduled_days * 100) if scheduled_days else 0.0, 2)
    return {
        "request_count": len(rows),
        "approved_days": approved_days,
        "rejected_days": rejected_days,
        "unplanned_days": unplanned_days,
        "leave_percentage": leave_percentage,
    }


def _leave_score(inputs: dict) -> float:
    excess = max(0.0, inputs["leave_percentage"] - settings.APPROVED_LEAVE_THRESHOLD_PERCENT)
    score = 100.0
    score -= excess * settings.APPROVED_LEAVE_EXCESS_PENALTY
    score -= inputs["unplanned_days"] * settings.UNPLANNED_LEAVE_PENALTY
    score -= inputs["rejected_days"] * settings.REJECTED_LEAVE_REQUEST_PENALTY
    return round(max(0.0, min(100.0, score)), 2)


def _calculate_overall(superior_rating: int, attendance_score: float, leave_score: float) -> float:
    return round((superior_rating * 0.60) + (attendance_score * 0.25) + (leave_score * 0.15), 2)


def _competition_rank(scores: list[float]) -> list[int]:
    ranks = []
    last_score = None
    last_rank = None
    for position, score in enumerate(scores, start=1):
        if last_score is not None and score == last_score:
            ranks.append(last_rank)
        else:
            ranks.append(position)
            last_rank = position
            last_score = score
    return ranks


def _apply_ranks(rows: list[MonthlyPerformance]):
    ranked = sorted([row for row in rows if row.overall_score is not None], key=lambda r: (-float(r.overall_score), r.employee_id))
    ranks = _competition_rank([float(row.overall_score) for row in ranked])
    rank_map = {row.id: rank for row, rank in zip(ranked, ranks)}
    for row in rows:
        row.rank = rank_map.get(row.id)


def recalculate_month_ranks(db: Session, performance_month: date):
    target = month_start(performance_month)
    rows = db.query(MonthlyPerformance).filter(
        MonthlyPerformance.performance_month == target,
        MonthlyPerformance.overall_score.is_not(None),
    ).all()
    _apply_ranks(rows)
    db.commit()


def _validate_evaluator_team(db: Session, actor: User, employee: Employee):
    actor_employee = _employee_for_user(db, actor)
    if actor.role != "Admin" and (not actor_employee or employee.superior_id != actor_employee.id):
        raise PermissionError("You can only evaluate employees currently assigned to your team")


def _snapshot_inputs(db: Session, employee: Employee, target_month: date):
    attendance = _attendance_inputs(db, employee, target_month)
    leave = _leave_inputs(db, employee.id, target_month, attendance["scheduled_days"])
    attendance_score = _attendance_score(attendance)
    leave_score = _leave_score(leave)
    return attendance, leave, attendance_score, leave_score


def upsert_monthly_evaluation(db: Session, actor: User, employee_id: int, performance_month: date, rating: int, feedback: str):
    if actor.role not in {"Superior", "CEO", "Admin"}:
        raise PermissionError("Only Superior, CEO, or Admin can submit evaluations")
    target_month = month_start(performance_month)
    if not evaluation_window_open(target_month):
        raise ValueError("Monthly evaluations can only be submitted from the 25th through the end of the month")

    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise ValueError("Employee not found")
    _validate_evaluator_team(db, actor, employee)

    existing = db.query(MonthlyPerformance).filter(
        MonthlyPerformance.employee_id == employee_id,
        MonthlyPerformance.performance_month == target_month,
    ).first()
    if existing and existing.status == "Finalized":
        raise PermissionError("Finalized performance records are read-only; use the controlled Admin correction workflow")

    attendance, leave, attendance_score, leave_score = _snapshot_inputs(db, employee, target_month)
    overall_score = _calculate_overall(rating, attendance_score, leave_score)

    if existing is None:
        existing = MonthlyPerformance(employee_id=employee_id, superior_id=employee.superior_id, performance_month=target_month)
        db.add(existing)
    existing.superior_id = employee.superior_id
    existing.superior_rating = rating
    existing.feedback = feedback
    existing.attendance_present_days = attendance["present_days"]
    existing.attendance_absent_days = attendance["absent_days"]
    existing.attendance_late_days = attendance["late_days"]
    existing.attendance_late_minutes = attendance["late_minutes"]
    existing.attendance_scheduled_days = attendance["scheduled_days"]
    existing.leave_request_count = leave["request_count"]
    existing.leave_approved_days = leave["approved_days"]
    existing.leave_rejected_days = leave["rejected_days"]
    existing.leave_unplanned_days = leave["unplanned_days"]
    existing.leave_percentage = leave["leave_percentage"]
    existing.attendance_score = attendance_score
    existing.leave_score = leave_score
    existing.overall_score = overall_score
    existing.status = "Submitted"
    existing.submitted_at = datetime.now(timezone.utc)
    if actor.role == "Admin" and existing.status == "Finalized":
        existing.finalized_at = existing.finalized_at
    db.flush()
    _audit(db, actor, "MONTHLY_EVALUATION_SUBMITTED", "MonthlyPerformance", existing.id,
           f"employee_id={employee_id}; month={target_month}; rating={rating}; overall={overall_score}")
    db.commit()
    recalculate_month_ranks(db, target_month)
    db.refresh(existing)
    return _serialize(existing)


def correct_finalized_evaluation(db: Session, admin: User, record_id: int, rating: int, feedback: str, reason: str):
    record = db.query(MonthlyPerformance).filter(MonthlyPerformance.id == record_id).first()
    if not record:
        raise ValueError("Performance record not found")
    if record.status != "Finalized":
        raise ValueError("Controlled correction is only available for finalized records")

    old = {"rating": record.superior_rating, "feedback": record.feedback, "overall_score": record.overall_score, "rank": record.rank}
    attendance_score = float(record.attendance_score or 0)
    leave_score = float(record.leave_score or 0)
    new_overall = _calculate_overall(rating, attendance_score, leave_score)
    record.superior_rating = rating
    record.feedback = feedback
    record.overall_score = new_overall
    record.corrected_at = datetime.now(timezone.utc)
    record.correction_count = int(record.correction_count or 0) + 1
    db.flush()
    _audit(
        db, admin, "FINALIZED_PERFORMANCE_CORRECTED", "MonthlyPerformance", record.id,
        f"reason={reason}; old={old}; new={{'rating': {rating}, 'feedback': {feedback!r}, 'overall_score': {new_overall}}}",
    )
    db.commit()
    recalculate_month_ranks(db, record.performance_month)
    db.refresh(record)
    return _serialize(record)


def finalize_month(db: Session, actor: User, performance_month: date):
    if actor.role != "Admin":
        raise PermissionError("Only Admin can finalize monthly performance records")
    target = month_start(performance_month)
    end = month_end(target)
    if business_today() <= end:
        raise ValueError("A month can only be finalized after its end date")

    employees = db.query(Employee).all()
    created_pending = finalized = 0
    for employee in employees:
        if employee.superior_id is None:
            continue
        record = db.query(MonthlyPerformance).filter(
            MonthlyPerformance.employee_id == employee.id,
            MonthlyPerformance.performance_month == target,
        ).first()
        if record is None:
            record = MonthlyPerformance(employee_id=employee.id, superior_id=employee.superior_id, performance_month=target, status="Pending Review")
            db.add(record)
            db.flush()
            created_pending += 1
        elif record.status != "Finalized" and record.superior_rating is not None:
            record.status = "Finalized"
            record.finalized_at = datetime.now(timezone.utc)
            finalized += 1
    _audit(db, actor, "MONTH_FINALIZED", "MonthlyPerformance", None,
           f"performance_month={target}; finalized={finalized}; pending_created={created_pending}")
    db.commit()
    recalculate_month_ranks(db, target)
    sync_pending_reviews(db, actor, target)
    return {"month": target, "finalized": finalized, "pending_created": created_pending}


def sync_pending_reviews(db: Session, actor: Optional[User], performance_month: Optional[date] = None):
    target = month_start(performance_month or previous_month())
    if business_today() <= month_end(target):
        return {"month": target, "pending": 0, "notifications": 0}

    employees = db.query(Employee).filter(Employee.superior_id.is_not(None)).all()
    pending = 0
    notifications = 0
    for employee in employees:
        record = db.query(MonthlyPerformance).filter(
            MonthlyPerformance.employee_id == employee.id,
            MonthlyPerformance.performance_month == target,
        ).first()
        if record is None:
            record = MonthlyPerformance(employee_id=employee.id, superior_id=employee.superior_id, performance_month=target, status="Pending Review")
            db.add(record)
            db.flush()
        if record.superior_rating is None:
            record.status = "Pending Review"
            pending += 1
            superior = db.query(Employee).filter(Employee.id == employee.superior_id).first()
            if superior:
                superior_user = _user_for_employee(db, superior)
                if superior_user:
                    title = "Pending Monthly Performance Review"
                    message = f"Monthly review for {employee.full_name} ({target.strftime('%B %Y')}) is still pending."
                    already = db.query(Notification).filter(
                        Notification.user_id == superior_user.id,
                        Notification.notification_type == "Performance",
                        Notification.title == title,
                        Notification.message == message,
                    ).first()
                    if not already:
                        db.add(Notification(user_id=superior_user.id, notification_type="Performance", title=title, message=message))
                        notifications += 1
    db.commit()
    if actor:
        _audit(db, actor, "PENDING_REVIEW_SYNC", "MonthlyPerformance", None,
               f"performance_month={target}; pending={pending}; notifications={notifications}")
        db.commit()
    return {"month": target, "pending": pending, "notifications": notifications}


def auto_finalize_previous_month(db: Session):
    target = previous_month()
    if business_today() == month_start(business_today()):
        admin_user = db.query(User).filter(User.role == "Admin").order_by(User.id).first()
        if admin_user:
            finalize_month(db, admin_user, target)
        return sync_pending_reviews(db, admin_user if 'admin_user' in locals() else None, target)
    return sync_pending_reviews(db, None, target)


def _serialize(row: MonthlyPerformance):
    return {
        "id": row.id,
        "employee_id": row.employee_id,
        "employee_name": row.employee.full_name if row.employee else None,
        "department": row.employee.department.department_name if row.employee and row.employee.department else None,
        "superior_id": row.superior_id,
        "superior_name": row.superior.full_name if row.superior else None,
        "performance_month": row.performance_month,
        "superior_rating": row.superior_rating,
        "feedback": row.feedback,
        "attendance_present_days": row.attendance_present_days,
        "attendance_absent_days": row.attendance_absent_days,
        "attendance_late_days": row.attendance_late_days,
        "attendance_late_minutes": row.attendance_late_minutes,
        "attendance_scheduled_days": row.attendance_scheduled_days,
        "leave_request_count": row.leave_request_count,
        "leave_approved_days": row.leave_approved_days,
        "leave_rejected_days": row.leave_rejected_days,
        "leave_unplanned_days": row.leave_unplanned_days,
        "leave_percentage": row.leave_percentage,
        "attendance_score": row.attendance_score,
        "leave_score": row.leave_score,
        "overall_score": row.overall_score,
        "rank": row.rank,
        "status": row.status,
        "correction_count": row.correction_count,
    }


def get_my_history(db: Session, user: User):
    employee = _employee_for_user(db, user)
    if not employee:
        raise ValueError("Employee profile not found")
    rows = db.query(MonthlyPerformance).options(joinedload(MonthlyPerformance.employee), joinedload(MonthlyPerformance.superior)).filter(
        MonthlyPerformance.employee_id == employee.id
    ).order_by(MonthlyPerformance.performance_month.desc()).all()
    return [_serialize(row) for row in rows]


def get_team_performance(db: Session, user: User, performance_month: Optional[date] = None):
    rows = get_team(db, user, performance_month)
    return rows


def _scope_rank(rows: list[MonthlyPerformance], scope: str, selected_department: Optional[int], selected_superior: Optional[int]):
    if scope == "department":
        if selected_department is None:
            raise ValueError("department_id is required for department ranking scope")
        groups = [r for r in rows if r.employee and r.employee.department_id == selected_department]
    elif scope == "superior":
        if selected_superior is None:
            raise ValueError("superior_id is required for Superior ranking scope")
        groups = [r for r in rows if r.superior_id == selected_superior]
    else:
        groups = rows
    _apply_ranks(groups)
    return groups


def get_insights(db: Session, user: User, performance_month: Optional[date], department_id=None, superior_id=None, employee_id=None, rank=None, ranking_scope="overall", sort_by="rank", sort_order="asc"):
    if user.role != "Admin":
        raise PermissionError("Only Admin can access organization-wide Performance Insights")
    target = month_start(performance_month or previous_month())
    if target != previous_month():
        raise ValueError("Performance Insights are published for the previous month")

    sync_pending_reviews(db, user, target)
    rows = db.query(MonthlyPerformance).options(
        joinedload(MonthlyPerformance.employee).joinedload(Employee.department),
        joinedload(MonthlyPerformance.superior),
    ).filter(MonthlyPerformance.performance_month == target).all()

    scoped = _scope_rank(rows, ranking_scope, department_id, superior_id)
    if employee_id is not None:
        scoped = [row for row in scoped if row.employee_id == employee_id]
    if department_id is not None:
        scoped = [row for row in scoped if row.employee and row.employee.department_id == department_id]
    if superior_id is not None:
        scoped = [row for row in scoped if row.superior_id == superior_id]
    if rank is not None:
        scoped = [row for row in scoped if row.rank == rank]

    data = [_serialize(row) for row in scoped]
    reverse = sort_order.lower() == "desc"
    key_map = {
        "rank": lambda x: (x["rank"] is None, x["rank"] if x["rank"] is not None else 999999),
        "overall_score": lambda x: (x["overall_score"] is None, x["overall_score"] if x["overall_score"] is not None else -1),
        "employee_name": lambda x: (x["employee_name"] or "").lower(),
        "department": lambda x: (x["department"] or "").lower(),
        "superior_name": lambda x: (x["superior_name"] or "").lower(),
    }
    if sort_by not in key_map:
        raise ValueError("Unsupported sort field")
    data.sort(key=key_map[sort_by], reverse=reverse)
    return data


def get_audit_logs(db: Session, limit=200):
    rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [{
        "id": row.id,
        "actor_user_id": row.actor_user_id,
        "action": row.action,
        "entity_type": row.entity_type,
        "entity_id": row.entity_id,
        "details": row.details,
        "created_at": row.created_at,
    } for row in rows]


def get_notifications(db: Session, user: User, unread_only: bool = False):
    query = db.query(Notification).filter(Notification.user_id == user.id)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    return [{
        "id": row.id,
        "notification_type": row.notification_type,
        "title": row.title,
        "message": row.message,
        "is_read": row.is_read,
        "created_at": row.created_at,
    } for row in query.order_by(Notification.created_at.desc()).limit(100).all()]


def mark_notification_read(db: Session, user: User, notification_id: int):
    row = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user.id).first()
    if not row:
        raise ValueError("Notification not found")
    row.is_read = True
    db.commit()
    return {"message": "Notification marked as read", "id": row.id}


def mark_all_notifications_read(db: Session, user: User):
    db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read.is_(False)).update({Notification.is_read: True}, synchronize_session=False)
    db.commit()
    return {"message": "All notifications marked as read"}


def get_retention_status(db: Session, user: User, employee_id: Optional[int] = None):
    if employee_id is None:
        employee = _employee_for_user(db, user)
        employee_id = employee.id if employee else None
    if not employee_id:
        raise ValueError("Employee profile not found")
    if user.role != "Admin":
        employee = _employee_for_user(db, user)
        if not employee or employee.id != employee_id:
            raise PermissionError("You can only view your own retention status")
    summary = retention_summary(db, employee_id)
    if not summary:
        raise ValueError("Employee not found")
    return summary
