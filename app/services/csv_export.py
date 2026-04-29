import csv
from io import StringIO

from app.models.license import ProfessionalLicense


CSV_HEADERS = [
    "crediva_license_id",
    "source_state",
    "source_agency",
    "license_type",
    "profession",
    "specialty",
    "license_number",
    "full_name",
    "business_name",
    "status",
    "status_raw",
    "issue_date",
    "expiration_date",
    "renewal_window_days",
    "renewal_window_bucket",
    "address_city",
    "address_state",
    "address_zip",
    "source_url",
    "source_fetched_at",
    "last_seen_at",
]


def _format(value: object) -> str:
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def licenses_to_csv(rows: list[ProfessionalLicense]) -> str:
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_HEADERS)
    writer.writeheader()

    for row in rows:
        writer.writerow(
            {
                "crediva_license_id": row.license_id,
                "source_state": row.source_state,
                "source_agency": row.source_agency,
                "license_type": row.license_type_code,
                "profession": row.profession,
                "specialty": row.specialty,
                "license_number": row.license_number,
                "full_name": row.full_name,
                "business_name": row.business_name,
                "status": row.status_normalized.value,
                "status_raw": row.status_raw,
                "issue_date": _format(row.issue_date),
                "expiration_date": _format(row.expiration_date),
                "renewal_window_days": row.renewal_window_days,
                "renewal_window_bucket": row.renewal_window_bucket,
                "address_city": row.address_city,
                "address_state": row.address_state,
                "address_zip": row.address_zip,
                "source_url": row.source_url,
                "source_fetched_at": _format(row.source_fetched_at),
                "last_seen_at": _format(row.last_seen_at),
            }
        )

    return buffer.getvalue()
