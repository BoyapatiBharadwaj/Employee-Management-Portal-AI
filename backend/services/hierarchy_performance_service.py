from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

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
)


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
    today = today or date.today()
    start = date(performance_month.year, performance_month.month, 25)
    end = month_end(performance_month)
    return start <= today <= end


def previous_month(value: Optional[date] = None) -> date:
    value = value or date.today()
    return add_months(month_start(value), -1)


def _employee_for_user(db: Session, user: User) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.email.ilike(user.email)).first()


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


def assign_superior(db: Session, actor: User, employee_id: int, superior_id: Optional[int], effective_from: date):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise ValueError("Employee not found")

    if superior_id is not None:
        superior = db.query(Employee).filter(Employee.id == superior_id).first()
        if not superior:
            raise ValueError("Superior not found")
        _ensure_no_cycle(db, employee_id, superior_id)
        if superior.id == employee.id:
            raise ValueError("An employee cannot report to themselves")

    previous = employee.superior_id
    if previous == superior_id:
        return employee

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
        db,
        actor,
        "SUPERIOR_CHANGED",
        "Employee",
        employee.id,
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


def get_team(db: Session, user: User):
    employee = _employee_for_user(db, user)
    if not employee:
        raise ValueError("Employee profile not found")
    rows = db.query(Employee).options(joinedload(Employee.department)).filter(Employee.superior_id == employee.id).order_by(Employee.full_name).all()
    return [{
        "id": emp.id,
        "employee_id": emp.employee_id,
        "full_name": emp.full_name,
        "email": emp.email,
        "department_id": emp.department_id,
        "department": emp.department.department_name if emp.department else None,
        "designation": emp.designation,
        "superior_id": emp.superior_id,
    } for emp in rows]


def _attendance_score(db: Session, employee_id: int, performance_month: date) -> float:
    start = month_start(performance_month)
    end = month_end(performance_month)
    rows = db.query(Attendance).filter(
        Attendance.employee_id == employee_id,
        Attendance.attendance_date.between(start, end),
    ).all()
    if not rows:
        return 100.0

    present = sum(1 for row in rows if str(row.status).lower() in {"present", "late", "half day", "half-day"})
    absent = sum(1 for row in rows if str(row.status).lower() == "absent")
    late_count = sum(1 for row in rows if (row.late_minutes or 0) > 0 or str(row.status).lower() == "late")
    total = present + absent
    base = (present / total * 100) if total else 100.0
    score = base - (late_count * settings.ATTENDANCE_LATE_PENALTY) - (absent * settings.ATTENDANCE_ABSENCE_PENALTY)
    return round(max(0.0, min(100.0, score)), 2)


def _leave_score(db: Session, employee_id: int, performance_month: date) -> float:
    start = month_start(performance_month)
    end = month_end(performance_month)
    rows = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.start_date <= end,
        LeaveRequest.end_date >= start,
    ).all()
    if not rows:
        return 100.0

    unplanned = 0
    total_leave_days = 0
    for row in rows:
        overlap_start = max(row.start_date, start)
        overlap_end = min(row.end_date, end)
        days = max(0, (overlap_end - overlap_start).days + 1)
        total_leave_days += days
        leave_type = (row.leave_type or "").lower()
        if "emergency" in leave_type or "unplanned" in leave_type:
            unplanned += days

    # Configurable normalization baseline: planned/approved leave does not itself reduce the score;
    # unplanned/emergency leave incurs the configured penalty.
    score = 100.0 - (unplanned * settings.UNPLANNED_LEAVE_PENALTY)
    return round(max(0.0, min(100.0, score)), 2)


def _calculate_overall(superior_rating: int, attendance_score: float, leave_score: float) -> float:
    return round(
        (superior_rating * 0.60) +
        (attendance_score * 0.25) +
        (leave_score * 0.15),
        2,
    )


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


def recalculate_month_ranks(db: Session, performance_month: date):
    target = month_start(performance_month)
    rows = db.query(MonthlyPerformance).filter(
        MonthlyPerformance.performance_month == target,
        MonthlyPerformance.overall_score.is_not(None),
    ).order_by(MonthlyPerformance.overall_score.desc(), MonthlyPerformance.employee_id.asc()).all()
    ranks = _competition_rank([float(row.overall_score) for row in rows])
    for row, rank in zip(rows, ranks):
        row.rank = rank
    db.commit()


def upsert_monthly_evaluation(db: Session, actor: User, employee_id: int, performance_month: date, rating: int, feedback: str):
    if actor.role not in {"Superior", "CEO", "Admin"}:
        raise PermissionError("Only Superior, CEO, or Admin can submit evaluations")
    target_month = month_start(performance_month)
    today = date.today()
    if actor.role != "Admin" and not evaluation_window_open(target_month, today):
        raise ValueError("Monthly evaluations can only be submitted from the 25th through the end of the month")

    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise ValueError("Employee not found")
    actor_employee = _employee_for_user(db, actor)
    if actor.role != "Admin" and (not actor_employee or employee.superior_id != actor_employee.id):
        raise PermissionError("You can only evaluate employees currently assigned to your team")

    existing = db.query(MonthlyPerformance).filter(
        MonthlyPerformance.employee_id == employee_id,
        MonthlyPerformance.performance_month == target_month,
    ).first()
    if existing and existing.status == "Finalized" and actor.role != "Admin":
        raise PermissionError("Finalized performance records are read-only")

    attendance_score = _attendance_score(db, employee_id, target_month)
    leave_score = _leave_score(db, employee_id, target_month)
    overall_score = _calculate_overall(rating, attendance_score, leave_score)

    if existing is None:
        existing = MonthlyPerformance(
            employee_id=employee_id,
            superior_id=employee.superior_id,
            performance_month=target_month,
        )
        db.add(existing)

    existing.superior_id = employee.superior_id
    existing.superior_rating = rating
    existing.feedback = feedback
    existing.attendance_score = attendance_score
    existing.leave_score = leave_score
    existing.overall_score = overall_score
    existing.status = "Submitted"
    existing.submitted_at = datetime.now(timezone.utc)
    db.flush()

    _audit(db, actor, "MONTHLY_EVALUATION_SUBMITTED", "MonthlyPerformance", existing.id,
           f"employee_id={employee_id}; month={target_month}; rating={rating}; overall={overall_score}")
    db.commit()
    recalculate_month_ranks(db, target_month)
    db.refresh(existing)
    return _serialize(existing)


def finalize_month(db: Session, actor: User, performance_month: date):
    if actor.role != "Admin":
        raise PermissionError("Only Admin can finalize monthly performance records")
    target = month_start(performance_month)
    end = month_end(target)
    today = date.today()
    if today <= end:
        raise ValueError("A month can only be finalized after its end date")

    employees = db.query(Employee).all()
    created_pending = 0
    finalized = 0
    for employee in employees:
        if employee.superior_id is None:
            continue
        record = db.query(MonthlyPerformance).filter(
            MonthlyPerformance.employee_id == employee.id,
            MonthlyPerformance.performance_month == target,
        ).first()
        if record is None:
            record = MonthlyPerformance(
                employee_id=employee.id,
                superior_id=employee.superior_id,
                performance_month=target,
                status="Pending Review",
            )
            db.add(record)
            db.flush()
            created_pending += 1
        elif record.status != "Finalized" and record.superior_rating is not None:
            record.status = "Finalized"
            record.finalized_at = datetime.now(timezone.utc)
            finalized += 1
    db.commit()
    recalculate_month_ranks(db, target)
    _audit(db, actor, "MONTH_FINALIZED", "MonthlyPerformance", None,
           f"performance_month={target}; finalized={finalized}; pending_created={created_pending}")
    db.commit()
    return {"month": target, "finalized": finalized, "pending_created": created_pending}


def sync_pending_reviews(db: Session, actor: Optional[User], performance_month: Optional[date] = None):
    target = month_start(performance_month or previous_month())
    if date.today() <= month_end(target):
        return {"month": target, "pending": 0, "notifications": 0}

    employees = db.query(Employee).filter(Employee.superior_id.is_not(None)).all()
    pending = []
    notifications = 0
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
        if record.superior_rating is None:
            record.status = "Pending Review"
            pending.append(record)
            superior = db.query(Employee).filter(Employee.id == employee.superior_id).first()
            if superior:
                superior_user = db.query(User).filter(User.email.ilike(superior.email)).first()
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
               f"performance_month={target}; pending={len(pending)}; notifications={notifications}")
        db.commit()
    return {"month": target, "pending": len(pending), "notifications": notifications}


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
        "attendance_score": row.attendance_score,
        "leave_score": row.leave_score,
        "overall_score": row.overall_score,
        "rank": row.rank,
        "status": row.status,
    }


def get_my_history(db: Session, user: User):
    employee = _employee_for_user(db, user)
    if not employee:
        raise ValueError("Employee profile not found")
    rows = db.query(MonthlyPerformance).options(joinedload(MonthlyPerformance.employee), joinedload(MonthlyPerformance.superior)).filter(
        MonthlyPerformance.employee_id == employee.id
    ).order_by(MonthlyPerformance.performance_month.desc()).all()
    return [_serialize(row) for row in rows]


def get_team_performance(db: Session, user: User):
    actor_employee = _employee_for_user(db, user)
    if not actor_employee and user.role != "Admin":
        raise ValueError("Employee profile not found")
    query = db.query(MonthlyPerformance).options(joinedload(MonthlyPerformance.employee), joinedload(MonthlyPerformance.superior))
    if user.role != "Admin":
        query = query.filter(MonthlyPerformance.superior_id == actor_employee.id)
    rows = query.order_by(MonthlyPerformance.performance_month.desc(), MonthlyPerformance.overall_score.desc().nullslast()).all()
    return [_serialize(row) for row in rows]


def get_insights(db: Session, user: User, performance_month: Optional[date], department_id=None, superior_id=None, employee_id=None, rank=None):
    if user.role != "Admin":
        raise PermissionError("Only Admin can access organization-wide Performance Insights")
    target = month_start(performance_month or previous_month())
    # Publication rule: only previous-month insights are published on the first day of the new month.
    if target != previous_month():
        raise ValueError("Performance Insights are published for the previous month")

    sync_pending_reviews(db, user, target)
    query = db.query(MonthlyPerformance).options(
        joinedload(MonthlyPerformance.employee).joinedload(Employee.department),
        joinedload(MonthlyPerformance.superior),
    ).filter(MonthlyPerformance.performance_month == target)
    if employee_id is not None:
        query = query.filter(MonthlyPerformance.employee_id == employee_id)
    if superior_id is not None:
        query = query.filter(MonthlyPerformance.superior_id == superior_id)
    if department_id is not None:
        query = query.join(MonthlyPerformance.employee).filter(Employee.department_id == department_id)
    rows = query.order_by(MonthlyPerformance.overall_score.desc().nullslast(), MonthlyPerformance.employee_id.asc()).all()
    result = [_serialize(row) for row in rows]
    if rank is not None:
        result = [row for row in result if row["rank"] == rank]
    return result


def get_audit_logs(db: Session, limit=100):
    rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [{
        "id": row.id,
        "action": row.action,
        "entity_type": row.entity_type,
        "entity_id": row.entity_id,
        "details": row.details,
        "created_at": row.created_at,
        "actor": row.actor.username if row.actor else None,
    } for row in rows]


def get_notifications(db: Session, user: User):
    rows = db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).limit(100).all()
    return [{
        "id": row.id,
        "notification_type": row.notification_type,
        "title": row.title,
        "message": row.message,
        "is_read": row.is_read,
        "created_at": row.created_at,
    } for row in rows]


def auto_finalize_previous_month(db: Session):
    target = previous_month()
    end = month_end(target)
    if date.today() <= end:
        return {"month": target, "finalized": 0, "pending_created": 0, "notifications": 0}

    employees = db.query(Employee).all()
    finalized = 0
    pending_created = 0
    notifications = 0
    for employee in employees:
        if employee.superior_id is None:
            continue
        record = db.query(MonthlyPerformance).filter(
            MonthlyPerformance.employee_id == employee.id,
            MonthlyPerformance.performance_month == target,
        ).first()
        if record is None:
            record = MonthlyPerformance(
                employee_id=employee.id,
                superior_id=employee.superior_id,
                performance_month=target,
                status="Pending Review",
            )
            db.add(record)
            db.flush()
            pending_created += 1
        elif record.status != "Finalized" and record.superior_rating is not None:
            record.status = "Finalized"
            record.finalized_at = datetime.now(timezone.utc)
            finalized += 1

        if record.superior_rating is None and employee.superior_id:
            superior = db.query(Employee).filter(Employee.id == employee.superior_id).first()
            if superior:
                superior_user = db.query(User).filter(User.email.ilike(superior.email)).first()
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
    recalculate_month_ranks(db, target)
    return {"month": target, "finalized": finalized, "pending_created": pending_created, "notifications": notifications}
