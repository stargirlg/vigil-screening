from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from app.models.alert import RiskLevel, AlertStatus


class AlertOut(BaseModel):
    id: UUID
    customer_id: UUID
    match_score: int
    params_matched: int
    matched_params: list
    match_details: dict
    risk_level: RiskLevel
    status: AlertStatus
    alert_type: Optional[str] = None
    assigned_to: Optional[UUID] = None
    reviewed_by: Optional[UUID] = None
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AlertReviewRequest(BaseModel):
    action: str        # CLEAR | CONFIRM | ESCALATE | REJECT
    notes: str
    assign_to: Optional[UUID] = None


class AlertSummary(BaseModel):
    total: int
    pending_review: int
    auto_closed: int
    confirmed_matches: int
    cleared: int
    escalated: int
    avg_tat_minutes: Optional[float] = None