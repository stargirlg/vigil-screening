import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


class WatchlistStatus(str, enum.Enum):
    FRAUD_CONFIRMED     = "FRAUD_CONFIRMED"
    SAR_FILED           = "SAR_FILED"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    PREVIOUS_ESCALATION = "PREVIOUS_ESCALATION"
    FALSE_POSITIVE      = "FALSE_POSITIVE"


class WatchlistEntry(Base):
    __tablename__ = "internal_watchlist"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id    = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    status         = Column(String(50), nullable=False)
    reason         = Column(Text, nullable=False)
    case_reference = Column(String(100), nullable=True)
    added_by       = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    added_by_email = Column(String(255), nullable=True)
    notes          = Column(Text, nullable=True)
    added_at       = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<WatchlistEntry {self.customer_id} [{self.status}]>"