"""
VIGIL — Screening Snapshot Model
Frozen record of what the system decided at a specific moment.
Critical for audit defensibility — rule changes cannot alter history.
Without this: cannot defend old decisions to RBI inspectors.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


class ScreeningSnapshot(Base):
    __tablename__ = "screening_snapshots"

    id                       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id              = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    alert_id                 = Column(UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=True)
    score                    = Column(Integer, nullable=False)
    risk_level               = Column(String(20), nullable=False)
    reasons                  = Column(JSON, nullable=False, default=list)
    rule_version             = Column(String(20), nullable=False, default="1.0")
    feature_weights_snapshot = Column(JSON, nullable=False, default=dict)
    watchlist_score          = Column(Integer, nullable=False, default=0)
    watchlist_status         = Column(String(50), nullable=True)
    param_results            = Column(JSON, nullable=False, default=dict)
    created_at               = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ScreeningSnapshot {self.customer_id} score={self.score} [{self.risk_level}]>"