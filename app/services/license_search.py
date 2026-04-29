from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.license import ProfessionalLicense
from app.schemas.license import LicenseSearchParams


def build_license_query(params: LicenseSearchParams) -> Select:
    query = select(ProfessionalLicense)

    if params.source_state:
        query = query.where(ProfessionalLicense.source_state == params.source_state.upper())
    if params.profession:
        query = query.where(ProfessionalLicense.profession.ilike(f"%{params.profession}%"))
    if params.license_type_code:
        query = query.where(ProfessionalLicense.license_type_code == params.license_type_code.upper())
    if params.status:
        query = query.where(ProfessionalLicense.status_normalized == params.status)
    if params.specialty:
        query = query.where(ProfessionalLicense.specialty.ilike(f"%{params.specialty}%"))
    if params.city:
        query = query.where(ProfessionalLicense.address_city.ilike(f"%{params.city}%"))
    if params.zip_code:
        query = query.where(ProfessionalLicense.address_zip == params.zip_code)
    if params.name:
        like = f"%{params.name}%"
        query = query.where(
            or_(
                ProfessionalLicense.full_name.ilike(like),
                ProfessionalLicense.business_name.ilike(like),
            )
        )
    if params.renewal_window_min is not None:
        query = query.where(ProfessionalLicense.renewal_window_days >= params.renewal_window_min)
    if params.renewal_window_max is not None:
        query = query.where(ProfessionalLicense.renewal_window_days <= params.renewal_window_max)
    if params.expires_from:
        query = query.where(ProfessionalLicense.expiration_date >= params.expires_from)
    if params.expires_to:
        query = query.where(ProfessionalLicense.expiration_date <= params.expires_to)

    return query


def search_licenses(db: Session, params: LicenseSearchParams) -> tuple[int, list[ProfessionalLicense]]:
    base = build_license_query(params)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.scalars(
        base.order_by(ProfessionalLicense.expiration_date.asc())
        .limit(params.limit)
        .offset(params.offset)
    ).all()
    return total, list(rows)
