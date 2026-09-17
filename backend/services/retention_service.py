from datetime import date
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from backend.models import Offboarding, Employee
from backend.config import settings


def employment_end_date(db: Session, employee_id: int):
    record = (
        db.query(Offboarding)
        .filter(Offboarding.employee_id == employee_id, Offboarding.last_working_day.isnot(None))
        .order_by(Offboarding.last_working_day.desc())
        .first()
    )
    return record.last_working_day if record else None


def retention_until(db: Session, employee_id: int):
    end = employment_end_date(db, employee_id)
    if end is None:
        return None
    return end + relativedelta(years=settings.RETENTION_YEARS)


def retention_blocks_deletion(db: Session, employee_id: int, today: date | None = None) -> bool:
    today = today or date.today()
    until = retention_until(db, employee_id)
    return until is None or until >= today


def retention_summary(db: Session, employee_id: int):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        return None
    end = employment_end_date(db, employee_id)
    until = retention_until(db, employee_id)
    return {
        "employee_id": employee.id,
        "employee_code": employee.employee_id,
        "employment_end_date": end,
        "retention_until": until,
        "retention_years": settings.RETENTION_YEARS,
        "protected": retention_blocks_deletion(db, employee_id),
    }
