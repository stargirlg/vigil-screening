from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from app.models.alert import RiskLevel


class ParamResult(BaseModel):
    matched: bool
    score: int
    detail: Optional[str] = None


class ScreeningResult(BaseModel):
    customer_id: UUID
    customer_name: str
    name: ParamResult
    dob: ParamResult
    id_check: ParamResult
    nationality: ParamResult
    occupation: ParamResult
    adverse_media: ParamResult
    pep: ParamResult
    matched_params: list[str]
    params_matched_count: int
    weighted_score: int
    risk_level: RiskLevel
    alert_type: Optional[str] = None
    is_false_alert: bool
    screened_at: datetime


class BatchScreenRequest(BaseModel):
    customer_ids: list[UUID]


class ScreeningStatus(BaseModel):
    task_id: str
    status: str
    total: Optional[int] = None
    processed: Optional[int] = None
    high_alerts: Optional[int] = None
    auto_closed: Optional[int] = None