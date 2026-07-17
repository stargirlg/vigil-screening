from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from app.models.rule import RuleStatus


class RuleCreate(BaseModel):
    name:        str
    param:       str
    weight:      int
    enabled:     bool = True
    threshold:   Optional[int] = None
    description: Optional[str] = None


class RuleUpdate(BaseModel):
    weight:      Optional[int] = None
    enabled:     Optional[bool] = None
    threshold:   Optional[int] = None
    description: Optional[str] = None


class RuleApproval(BaseModel):
    approved: bool
    notes:    str


class RuleOut(BaseModel):
    id:               UUID
    name:             str
    param:            str
    weight:           int
    enabled:          bool
    threshold:        Optional[int] = None
    description:      Optional[str] = None
    status:           str
    version:          int
    rule_set_version: str
    created_by_email: Optional[str] = None
    approved_by_email: Optional[str] = None
    approved_at:      Optional[datetime] = None
    created_at:       datetime

    model_config = {"from_attributes": True}


class RuleVersionOut(BaseModel):
    id:               UUID
    rule_id:          UUID
    version:          int
    rule_set_version: str
    snapshot:         dict
    changed_by_email: Optional[str] = None
    change_reason:    Optional[str] = None
    created_at:       datetime

    model_config = {"from_attributes": True}