from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.monitor import RenewalMonitor
from app.schemas.monitor import RenewalMonitorCreate, RenewalMonitorRead

router = APIRouter(prefix="/monitors", tags=["renewal monitors"])


@router.post("", response_model=RenewalMonitorRead, status_code=201)
def create_monitor(payload: RenewalMonitorCreate, db: Session = Depends(get_db)) -> RenewalMonitor:
    monitor = RenewalMonitor(**payload.model_dump())
    db.add(monitor)
    db.commit()
    db.refresh(monitor)
    return monitor


@router.get("", response_model=list[RenewalMonitorRead])
def list_monitors(account_id: str, db: Session = Depends(get_db)) -> list[RenewalMonitor]:
    return list(
        db.scalars(
            select(RenewalMonitor)
            .where(RenewalMonitor.account_id == account_id)
            .order_by(RenewalMonitor.created_at.desc())
        ).all()
    )
