"""
VIGIL — Case Model
Alert → Case → Investigation → Evidence → Decision → Closure
This is what makes VIGIL a compliance PLATFORM not just a screening tool.
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


class CaseStatus(str, enum.Enum):
    OPEN             = "OPEN"
    INVESTIGATING    = "INVESTIGATING"
    PENDING_CO       = "PENDING_CO"
    CLOSED           = "CLOSED"


class CaseDecision(str, enum.Enum):
    CONFIRMED_MATCH  = "CONFIRMED_MATCH"
    FALSE_POSITIVE   = "FALSE_POSITIVE"
    SAR_FILED        = "SAR_FILED"
    ESCALATED        = "ESCALATED"


class Case(Base):
    __tablename__ = "cases"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_number      = Column(String(50), unique=True, nullable=False)
    alert_id         = Column(UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=False, index=True)
    customer_id      = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)

    # Status tracking
    status           = Column(String(50), nullable=False, default=CaseStatus.OPEN)

    # Assignment
    assigned_to      = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_email   = Column(String(255), nullable=True)

    # Four-eyes — analyst recommends, CO decides
    analyst_recommendation = Column(String(50), nullable=True)
    analyst_notes          = Column(Text, nullable=True)
    analyst_id             = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    analyst_submitted_at   = Column(DateTime, nullable=True)

    # CO final decision
    co_decision      = Column(String(50), nullable=True)
    co_notes         = Column(Text, nullable=True)
    co_id            = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    co_decided_at    = Column(DateTime, nullable=True)

    # SAR flag
    sar_required     = Column(Boolean, default=False, nullable=False)
    sar_filed_at     = Column(DateTime, nullable=True)

    # Decision locking — after CO decision, case is frozen
    decision_locked  = Column(Boolean, default=False, nullable=False)

    # Rule version at time of case creation
    rule_version     = Column(String(20), nullable=False, default="1.0")

    # SLA
    sla_deadline     = Column(DateTime, nullable=True)
    sla_breached     = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at       = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at        = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Case {self.case_number} [{self.status}]>"


class CaseNote(Base):
    __tablename__ = "case_notes"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id     = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True)
    author_id   = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    author_email = Column(String(255), nullable=True)
    note        = Column(Text, nullable=False)
    note_type   = Column(String(50), default="GENERAL")  # GENERAL | EVIDENCE | DECISION
    created_at  = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<CaseNote {self.case_id} by {self.author_email}>"


class CaseEvidence(Base):
    __tablename__ = "case_evidence"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id      = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True)
    uploaded_by  = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    uploader_email = Column(String(255), nullable=True)
    file_name    = Column(String(255), nullable=False)
    file_type    = Column(String(50), nullable=True)
    description  = Column(Text, nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<CaseEvidence {self.file_name} for case {self.case_id}>"


class CaseDecisionLog(Base):
    __tablename__ = "case_decisions"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id     = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True)
    decided_by  = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    decider_email = Column(String(255), nullable=True)
    decision    = Column(String(50), nullable=False)
    notes       = Column(Text, nullable=True)
    rule_version = Column(String(20), nullable=False, default="1.0")
    decided_at  = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<CaseDecision {self.decision} by {self.decider_email}>"