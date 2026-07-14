import uuid

from sqlalchemy import Column, Date, DateTime, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID

from db.database import Base


class HistoricalTransaction(Base):
    __tablename__ = "historical_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    category = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "transaction_date", "description", "amount",
            name="uq_transaction_dedupe",
        ),
    )


class SystemConfig(Base):
    __tablename__ = "system_config"

    key = Column(String, primary_key=True)
    value = Column(Numeric(14, 2), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    starting_cash = Column(Numeric(14, 2), nullable=False)
    revenue_growth_pct = Column(Numeric(6, 2), nullable=False)
    num_new_hires = Column(Numeric(6, 0), nullable=False)
    avg_monthly_salary = Column(Numeric(14, 2), nullable=False)
    overhead_increase_pct = Column(Numeric(6, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UploadAuditLog(Base):
    __tablename__ = "upload_audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    uploaded_by = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    rows_inserted = Column(Integer, nullable=False)
    rows_duplicate = Column(Integer, nullable=False)
    rows_rejected = Column(Integer, nullable=False)
