from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RenewalMonitorCreate(BaseModel):
    account_id: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=160)
    filters: dict
    window_days: int = Field(default=60, ge=1, le=365)


class RenewalMonitorRead(BaseModel):
    monitor_id: str
    account_id: str
    name: str
    filters: dict
    window_days: int
    is_active: bool
    last_run_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
