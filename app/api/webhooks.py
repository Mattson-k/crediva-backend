from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class RenewalWebhookPreviewRequest(BaseModel):
    account_id: str
    saved_search_id: str
    saved_search_name: str
    owner_id: str
    window_days: int = Field(default=60, ge=1, le=365)
    license_id: str
    source_state: str
    source_agency: str
    license_number: str
    license_type: str
    profession: str
    full_name: str
    expiration_date: str
    source_url: str
    specialty: Optional[str] = None


@router.post("/renewal-preview")
def renewal_webhook_preview(payload: RenewalWebhookPreviewRequest) -> dict:
    return {
        "event_type": "license.renewal_window.entered",
        "event_id": f"evt_{uuid4().hex}",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "account_id": payload.account_id,
        "trigger": {
            "window_days": payload.window_days,
            "saved_search_id": payload.saved_search_id,
            "saved_search_name": payload.saved_search_name,
        },
        "license": {
            "crediva_license_id": payload.license_id,
            "source_state": payload.source_state,
            "source_agency": payload.source_agency,
            "license_number": payload.license_number,
            "license_type": payload.license_type,
            "profession": payload.profession,
            "specialty": payload.specialty,
            "full_name": payload.full_name,
            "status": "active",
            "expiration_date": payload.expiration_date,
            "renewal_window_days": payload.window_days,
            "source_url": payload.source_url,
        },
        "crm": {
            "provider": "salesforce",
            "owner_id": payload.owner_id,
            "object": "Task",
            "action": "create",
            "subject": (
                f"Renewal opportunity: {payload.full_name}, "
                f"{payload.source_state} {payload.license_type} expires in {payload.window_days} days"
            ),
            "priority": "High",
        },
    }
