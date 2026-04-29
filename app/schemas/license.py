from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.license import LicenseStatus


class LicenseSearchParams(BaseModel):
    source_state: Optional[str] = Field(default=None, min_length=2, max_length=2)
    profession: Optional[str] = None
    license_type_code: Optional[str] = None
    status: Optional[LicenseStatus] = None
    specialty: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None
    name: Optional[str] = None
    renewal_window_min: Optional[int] = None
    renewal_window_max: Optional[int] = None
    expires_from: Optional[date] = None
    expires_to: Optional[date] = None
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class LicenseRead(BaseModel):
    license_id: str
    source_state: str
    source_agency: str
    source_url: str
    source_record_id: str
    license_number: str
    license_type_code: str
    profession: str
    specialty: Optional[str]
    full_name: str
    business_name: Optional[str]
    status_raw: str
    status_normalized: LicenseStatus
    issue_date: Optional[date]
    expiration_date: date
    renewal_window_days: int
    renewal_window_bucket: str
    address_city: Optional[str]
    address_state: Optional[str]
    address_zip: Optional[str]
    last_seen_at: datetime
    first_seen_at: datetime
    source_fetched_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LicenseSearchResponse(BaseModel):
    total: int
    limit: int
    offset: int
    results: list[LicenseRead]
