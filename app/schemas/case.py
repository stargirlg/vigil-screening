from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class CaseCreate(BaseModel):
    alert_id: UUID
    customer_id: UUID
    assigned_to: Optional[UUID] = None


class CaseOut(BaseModel):
    id: UUID
    case_number: str
    alert_id: UUID
    customer_id: UUID
    status: str
    assigned_email: Optional[str] = None
    analyst_recommendation: Optional[str] = None
    analyst_notes: Optional[str] = None
    co_decision: Optional[str] = None
    co_notes: Optional[str] = None
    sar_required: bool
    decision_locked: bool
    rule_version: str
    sla_deadline: Optional[datetime] = None
    sla_breached: bool
    created_at: datetime
    closed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CaseNoteCreate(BaseModel):
    note: str
    note_type: str = "GENERAL"


class CaseNoteOut(BaseModel):
    id: UUID
    case_id: UUID
    author_email: Optional[str] = None
    note: str
    note_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalystRecommendation(BaseModel):
    recommendation: str    # CONFIRMED_MATCH | FALSE_POSITIVE | NEEDS_ESCALATION
    notes: str


class CODecision(BaseModel):
    decision: str          # CONFIRMED_MATCH | FALSE_POSITIVE | SAR_FILED
    notes: str
    sar_required: bool = False


class CaseEvidenceOut(BaseModel):
    id: UUID
    case_id: UUID
    uploader_email: Optional[str] = None
    file_name: str
    file_type: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}