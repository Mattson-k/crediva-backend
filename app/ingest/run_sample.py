from sqlalchemy import select

from app.db.session import Base, SessionLocal, engine
from app.ingest.normalizer import normalize_license
from app.ingest.sources.sample import SampleLicenseSource
from app.models.license import ProfessionalLicense


def upsert_sample() -> int:
    Base.metadata.create_all(bind=engine)
    source = SampleLicenseSource()
    rows = [normalize_license(raw) for raw in source.fetch()]

    with SessionLocal() as db:
        for row in rows:
            existing = db.scalar(
                select(ProfessionalLicense).where(
                    ProfessionalLicense.source_state == row.source_state,
                    ProfessionalLicense.license_type_code == row.license_type_code,
                    ProfessionalLicense.license_number == row.license_number,
                )
            )
            if existing:
                for field in [
                    "source_agency",
                    "source_url",
                    "source_record_id",
                    "profession",
                    "specialty",
                    "full_name",
                    "business_name",
                    "status_raw",
                    "status_normalized",
                    "issue_date",
                    "expiration_date",
                    "renewal_window_days",
                    "renewal_window_bucket",
                    "address_city",
                    "address_state",
                    "address_zip",
                    "last_seen_at",
                    "source_fetched_at",
                    "record_hash",
                ]:
                    setattr(existing, field, getattr(row, field))
            else:
                db.add(row)
        db.commit()
    return len(rows)


if __name__ == "__main__":
    print(f"upserted={upsert_sample()}")
