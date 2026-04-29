from datetime import date, datetime
from enum import Enum as PythonEnum
from typing import Optional
from uuid import uuid4

from sqlalchemy import Date, DateTime, Enum as SqlEnum, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class LicenseStatus(str, PythonEnum):
    active = "active"
    expired = "expired"
    suspended = "suspended"
    revoked = "revoked"
    pending = "pending"
    unknown = "unknown"


class ProfessionalLicense(Base):
    __tablename__ = "professional_licenses"
    __table_args__ = (
        UniqueConstraint(
            "source_state",
            "license_type_code",
            "license_number",
            name="uq_license_state_type_number",
        ),
        Index("idx_license_core_filter", "profession", "source_state", "expiration_date"),
        Index("idx_license_type_state_exp", "license_type_code", "source_state", "expiration_date"),
        Index("idx_license_status_exp", "status_normalized", "expiration_date"),
        Index("idx_license_renewal_bucket", "renewal_window_bucket", "source_state", "profession"),
        Index("idx_license_location", "source_state", "address_city", "address_zip"),
    )

    license_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    source_state: Mapped[str] = mapped_column(String(2), nullable=False)
    source_agency: Mapped[str] = mapped_column(String(200), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_record_id: Mapped[str] = mapped_column(String(120), nullable=False)
    license_number: Mapped[str] = mapped_column(String(80), nullable=False)
    license_type_code: Mapped[str] = mapped_column(String(30), nullable=False)
    profession: Mapped[str] = mapped_column(String(120), nullable=False)
    specialty: Mapped[Optional[str]] = mapped_column(String(160))
    full_name: Mapped[str] = mapped_column(String(240), nullable=False)
    business_name: Mapped[Optional[str]] = mapped_column(String(240))
    status_raw: Mapped[str] = mapped_column(String(120), nullable=False)
    status_normalized: Mapped[LicenseStatus] = mapped_column(
        SqlEnum(LicenseStatus), nullable=False, default=LicenseStatus.unknown
    )
    issue_date: Mapped[Optional[date]] = mapped_column(Date)
    expiration_date: Mapped[date] = mapped_column(Date, nullable=False)
    renewal_window_days: Mapped[int] = mapped_column(Integer, nullable=False)
    renewal_window_bucket: Mapped[str] = mapped_column(String(30), nullable=False)
    address_city: Mapped[Optional[str]] = mapped_column(String(120))
    address_state: Mapped[Optional[str]] = mapped_column(String(2))
    address_zip: Mapped[Optional[str]] = mapped_column(String(20))
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    record_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
