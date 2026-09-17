"""Idempotent database upgrade helper for the hierarchy/performance release."""
from sqlalchemy import inspect, text

from backend.database import Base, engine
import backend.models  # noqa: F401 - registers all models with Base.metadata


def upgrade():
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    if "employees" not in tables:
        # Fresh database: create the complete current schema.
        Base.metadata.create_all(bind=engine)
        return

    columns = {column["name"] for column in inspector.get_columns("employees")}
    if "superior_id" not in columns:
        with engine.begin() as connection:
            connection.execute(text(
                'ALTER TABLE employees ADD COLUMN superior_id INTEGER '
                'REFERENCES employees(id) ON DELETE SET NULL'
            ))
            connection.execute(text(
                'CREATE INDEX IF NOT EXISTS ix_employees_superior_id ON employees(superior_id)'
            ))

    # Create any new tables that are not present on an older deployment.
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    upgrade()
    print("Database upgrade completed.")
