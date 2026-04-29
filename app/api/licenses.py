from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.license import LicenseStatus
from app.schemas.license import LicenseSearchParams, LicenseSearchResponse
from app.services.csv_export import licenses_to_csv
from app.services.license_search import search_licenses

router = APIRouter(prefix="/licenses", tags=["licenses"])


def _params(
    source_state: Optional[str] = Query(default=None, min_length=2, max_length=2),
    profession: Optional[str] = None,
    license_type_code: Optional[str] = None,
    status: Optional[LicenseStatus] = None,
    specialty: Optional[str] = None,
    city: Optional[str] = None,
    zip_code: Optional[str] = None,
    name: Optional[str] = None,
    renewal_window_min: Optional[int] = None,
    renewal_window_max: Optional[int] = None,
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> LicenseSearchParams:
    return LicenseSearchParams(
        source_state=source_state,
        profession=profession,
        license_type_code=license_type_code,
        status=status,
        specialty=specialty,
        city=city,
        zip_code=zip_code,
        name=name,
        renewal_window_min=renewal_window_min,
        renewal_window_max=renewal_window_max,
        limit=limit,
        offset=offset,
    )


@router.get("", response_model=LicenseSearchResponse)
def list_licenses(
    params: LicenseSearchParams = Depends(_params),
    db: Session = Depends(get_db),
) -> LicenseSearchResponse:
    total, rows = search_licenses(db, params)
    return LicenseSearchResponse(total=total, limit=params.limit, offset=params.offset, results=rows)


@router.get("/export.csv")
def export_licenses(
    params: LicenseSearchParams = Depends(_params),
    db: Session = Depends(get_db),
) -> Response:
    total, rows = search_licenses(db, params)
    content = licenses_to_csv(rows)
    filename = "crediva_export.csv"
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Crediva-Total-Matches": str(total),
            "X-Crediva-Exported-Rows": str(len(rows)),
        },
    )
