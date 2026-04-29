import hashlib
from datetime import date, datetime, timezone
from typing import Optional

from app.models.license import LicenseStatus, ProfessionalLicense
from app.services.renewal import renewal_bucket, renewal_window_days


STATUS_MAP = {
    "active": LicenseStatus.active,
    "current": LicenseStatus.active,
    "licensed": LicenseStatus.active,
    "clear": LicenseStatus.active,
    "expired": LicenseStatus.expired,
    "delinquent": LicenseStatus.expired,
    "suspended": LicenseStatus.suspended,
    "revoked": LicenseStatus.revoked,
    "pending": LicenseStatus.pending,
}


def normalize_status(status_raw: str) -> LicenseStatus:
    lowered = status_raw.strip().lower()
    for token, normalized in STATUS_MAP.items():
        if token in lowered:
            return normalized
    return LicenseStatus.unknown


def record_hash(payload: dict) -> str:
    material = "|".join(str(payload.get(key, "")) for key in sorted(payload))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def normalize_license(raw: dict, today: Optional[date] = None) -> ProfessionalLicense:
    today = today or date.today()
    expiration_date = raw["expiration_date"]
    days = renewal_window_days(expiration_date, today=today)
    fetched_at = raw.get("source_fetched_at") or datetime.now(timezone.utc)
    status = normalize_status(raw["status_raw"])

    return ProfessionalLicense(
        source_state=raw["source_state"].upper(),
        source_agency=raw["source_agency"],
        source_url=raw["source_url"],
        source_record_id=raw["source_record_id"],
        license_number=raw["license_number"].strip().upper(),
        license_type_code=raw["license_type_code"].upper(),
        profession=raw["profession"],
        specialty=raw.get("specialty"),
        full_name=raw["full_name"],
        business_name=raw.get("business_name"),
        status_raw=raw["status_raw"],
        status_normalized=status,
        issue_date=raw.get("issue_date"),
        expiration_date=expiration_date,
        renewal_window_days=days,
        renewal_window_bucket=renewal_bucket(days),
        address_city=raw.get("address_city"),
        address_state=raw.get("address_state"),
        address_zip=raw.get("address_zip"),
        first_seen_at=fetched_at,
        last_seen_at=fetched_at,
        source_fetched_at=fetched_at,
        record_hash=record_hash(raw),
    )
