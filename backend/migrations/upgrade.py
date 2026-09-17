"""Idempotent schema migration helper for local/Docker deployments."""
from sqlalchemy import inspect, text

from backend.database import Base, engine
import backend.models  # noqa: F401


def _add_column(connection, table: str, column: str, ddl: str, existing_columns: set[str]):
    if column not in existing_columns:
        connection.execute(text(f'ALTER TABLE {table} ADD COLUMN {column} {ddl}'))


def upgrade():
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    if "employees" not in tables:
        Base.metadata.create_all(bind=engine)
    else:
        with engine.begin() as connection:
            employee_columns = {c["name"] for c in inspector.get_columns("employees")}
            _add_column(connection, "employees", "superior_id", "INTEGER REFERENCES employees(id) ON DELETE SET NULL", employee_columns)
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_employees_superior_id ON employees(superior_id)"))

    inspector = inspect(engine)
    with engine.begin() as connection:
        # New monthly-performance snapshot fields.
        if "monthly_performance" in inspector.get_table_names():
            columns = {c["name"] for c in inspector.get_columns("monthly_performance")}
            additions = {
                "attendance_present_days": "INTEGER",
                "attendance_absent_days": "INTEGER",
                "attendance_late_days": "INTEGER",
                "attendance_late_minutes": "INTEGER",
                "attendance_scheduled_days": "INTEGER",
                "leave_request_count": "INTEGER",
                "leave_approved_days": "INTEGER",
                "leave_rejected_days": "INTEGER",
                "leave_unplanned_days": "INTEGER",
                "leave_percentage": "DOUBLE PRECISION",
                "corrected_at": "TIMESTAMPTZ",
                "correction_count": "INTEGER NOT NULL DEFAULT 0",
            }
            for name, ddl in additions.items():
                _add_column(connection, "monthly_performance", name, ddl, columns)
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_mp_month_overall ON monthly_performance(performance_month, overall_score DESC)"))

        connection.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_active_employee_superior "
            "ON employee_superior_history(employee_id) WHERE effective_to IS NULL"
        ))
        # DB-level integrity checks where supported by PostgreSQL.
        connection.execute(text("DO $$ BEGIN ALTER TABLE employees ADD CONSTRAINT ck_employee_not_own_superior CHECK (superior_id IS NULL OR superior_id <> id); EXCEPTION WHEN duplicate_object THEN NULL; END $$;"))
        connection.execute(text("DO $$ BEGIN ALTER TABLE employee_superior_history ADD CONSTRAINT ck_history_dates CHECK (effective_to IS NULL OR effective_to >= effective_from); EXCEPTION WHEN duplicate_object THEN NULL; END $$;"))
        connection.execute(text("DO $$ BEGIN ALTER TABLE monthly_performance ADD CONSTRAINT ck_mp_status CHECK (status IN ('Pending Review','Submitted','Finalized')); EXCEPTION WHEN duplicate_object THEN NULL; END $$;"))
        connection.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_audit_entity_created "
            "ON audit_logs(entity_type, entity_id, created_at DESC)"
        ))
        connection.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_notifications_user_read_created "
            "ON notifications(user_id, is_read, created_at DESC)"
        ))

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    upgrade()
    print("Database upgrade completed.")
