"""
VIGIL — Rule Engine Model
Rules stored in DB — configurable without code changes.
Maker-checker: Admin creates → CO approves → rule goes live.
Rule versioning: every change creates a new version snapshot.
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


class RuleStatus(str, enum.Enum):
    DRAFT    = "DRAFT"      # Created by admin, not yet approved
    ACTIVE   = "ACTIVE"     # Approved by CO, in use
    INACTIVE = "INACTIVE"   # Disabled
    REJECTED = "REJECTED"   # CO rejected


class Rule(Base):
    __tablename__ = "rules"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name         = Column(String(100), nullable=False, unique=True)
    param        = Column(String(50), nullable=False)   # name | dob | id | nationality | occupation | adverse_media | pep | watchlist
    weight       = Column(Integer, nullable=False)       # 0-100
    enabled      = Column(Boolean, default=True, nullable=False)
    threshold    = Column(Integer, nullable=True)        # fuzzy threshold for name param
    description  = Column(Text, nullable=True)
    status       = Column(String(20), nullable=False, default=RuleStatus.DRAFT)
    version      = Column(Integer, nullable=False, default=1)
    rule_set_version = Column(String(20), nullable=False, default="1.0")

    # Maker
    created_by       = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by_email = Column(String(255), nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Checker (CO approval)
    approved_by       = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_by_email = Column(String(255), nullable=True)
    approved_at       = Column(DateTime, nullable=True)
    approval_notes    = Column(Text, nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Rule {self.name} [{self.param}] w={self.weight} [{self.status}]>"


class RuleVersion(Base):
    """
    Immutable snapshot of a rule at a point in time.
    Auditors can ask: what rules were active on date X?
    """
    __tablename__ = "rule_versions"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id          = Column(UUID(as_uuid=True), ForeignKey("rules.id"), nullable=False, index=True)
    version          = Column(Integer, nullable=False)
    rule_set_version = Column(String(20), nullable=False)
    snapshot         = Column(JSON, nullable=False)   # full rule state at this version
    changed_by       = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    changed_by_email = Column(String(255), nullable=True)
    change_reason    = Column(Text, nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<RuleVersion rule={self.rule_id} v={self.version}>"