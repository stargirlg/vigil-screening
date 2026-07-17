import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum as SAEnum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertStatus(str, enum.Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    AUTO_CLOSED = "AUTO_CLOSED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ESCALATED = "ESCALATED"
    CLEARED = "CLEARED"
    CONFIRMED_MATCH = "CONFIRMED_MATCH"
    REJECTED = "REJECTED"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)

    # Scoring
    match_score = Column(Integer, nullable=False)
    params_matched = Column(Integer, nullable=False)
    matched_params = Column(JSON, nullable=False, default=list)
    match_details = Column(JSON, nullable=False, default=dict)

    # Classification
    risk_level = Column(SAEnum(RiskLevel), nullable=False, default=RiskLevel.LOW)
    status = Column(SAEnum(AlertStatus), nullable=False, default=AlertStatus.PENDING_REVIEW)
    alert_type = Column(String(50), nullable=True)

    # Workflow
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    review_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    # TAT tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    def tat_minutes(self) -> float | None:
        if self.closed_at and self.created_at:
            return (self.closed_at - self.created_at).total_seconds() / 60
        return None

    def __repr__(self):
        return f"<Alert {self.id} [{self.risk_level}] {self.status}>"