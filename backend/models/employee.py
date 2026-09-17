from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Date
from backend.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        String(20),
        unique=True,
        nullable=False
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False
    )

    department_id = Column(
        Integer,
        ForeignKey("departments.id")
    )

    designation = Column(
        String(100),
        nullable=False
    )

    salary = Column(
        Float,
        nullable=False
    )

    department = relationship(
        "Department",
        back_populates="employees"
    )

    performance_records = relationship(
    "Performance",
    back_populates="employee",
    cascade="all, delete"
    )

    onboarding_records = relationship(
    "Onboarding",
    back_populates="employee",
    cascade="all, delete"
    )

    offboarding_records = relationship(
    "Offboarding",
    back_populates="employee",
    cascade="all, delete"
    )
    documents = relationship(
    "EmployeeDocument",
    back_populates="employee",
    cascade="all, delete"
    )
    phone = Column(
    String(20),
    nullable=True
    )

    address = Column(
    String(300),
    nullable=True
    )

    emergency_contact = Column(
    String(20),
    nullable=True
    )

    date_of_birth = Column(
    Date,
    nullable=True
    )

    joining_date = Column(
    Date,
    nullable=True
    )

    nationality = Column(
    String(50),
    nullable=True
    )

    profile_photo = Column(
    String(255),
    nullable=True
    )

    superior_id = Column(
    Integer,
    ForeignKey("employees.id", ondelete="SET NULL"),
    nullable=True,
    index=True
    )

    superior = relationship(
    "Employee",
    remote_side=[id],
    foreign_keys=[superior_id],
    backref="direct_reports"
    )

    superior_history = relationship(
    "EmployeeSuperiorHistory",
    foreign_keys="EmployeeSuperiorHistory.employee_id",
    back_populates="employee",
    cascade="all, delete",
    passive_deletes=True
    )
