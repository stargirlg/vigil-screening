from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from app.models.watchlist import WatchlistStatus


class WatchlistCreate(BaseModel):
    customer_id:    UUID
    status:         WatchlistStatus
    reason:         str
    case_reference: Optional[str] = None
    notes:          Optional[str] = None


class WatchlistOut(BaseModel):
    id:             UUID
    customer_id:    UUID
    status:         str
    reason:         str
    case_reference: Optional[str] = None
    added_by_email: Optional[str] = None
    notes:          Optional[str] = None
    added_at:       datetime

    model_config = {"from_attributes": True}


class WatchlistCheckResult(BaseModel):
    found:          bool
    status:         Optional[str] = None
    entries:        list
    score_override: Optional[int] = None
    score_addition: int
    impact:         str
    reason:         str