import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


class SanctionEntry(Base):
    __tablename__ = "sanction_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(20), nullable=False, index=True)
    source_id = Column(String(100), nullable=True)
    full_name = Column(String(255), nullable=False, index=True)
    aliases = Column(JSON, default=list)
    dob = Column(Date, nullable=True)
    nationality = Column(String(100), nullable=True)
    occupation = Column(String(255), nullable=True)
    pan = Column(String(20), nullable=True)
    passport = Column(String(20), nullable=True)
    national_id = Column(String(50), nullable=True)
    program = Column(String(255), nullable=True)
    reason = Column(Text, nullable=True)
    listing_date = Column(Date, nullable=True)
    imported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(String(5), default="true")

    def __repr__(self):
        return f"<SanctionEntry {self.full_name} [{self.source}]>"