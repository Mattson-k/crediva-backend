from datetime import date, datetime, timedelta, timezone
from typing import Optional

from app.ingest.sources.base import LicenseSource


class SampleLicenseSource(LicenseSource):
    source_state = "TX"
    source_agency = "Texas Medical Board"
    license_type_codes = ("MD",)

    def fetch(self, since: Optional[date] = None) -> list[dict]:
        today = date.today()
        return [
            {
                "source_state": "TX",
                "source_agency": self.source_agency,
                "source_url": "https://www.tmb.texas.gov/page/look-up-a-license",
                "source_record_id": "sample-md-001",
                "license_number": "M12345",
                "license_type_code": "MD",
                "profession": "Physician",
                "specialty": "Dermatology",
                "full_name": "Jane A. Smith",
                "business_name": "Lone Star Dermatology",
                "status_raw": "Active",
                "issue_date": today.replace(year=today.year - 8),
                "expiration_date": today + timedelta(days=60),
                "address_city": "Austin",
                "address_state": "TX",
                "address_zip": "78701",
                "source_fetched_at": datetime.now(timezone.utc),
            }
        ]
