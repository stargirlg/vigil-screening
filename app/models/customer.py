import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(100), nullable=True, index=True)

    # 7 Screening Parameters
    full_name = Column(String(255), nullable=False, index=True)   # Param 1
    dob = Column(Date, nullable=True)                              # Param 2
    pan = Column(String(20), nullable=True, index=True)            # Param 3a
    aadhaar = Column(String(20), nullable=True)                    # Param 3b
    passport = Column(String(20), nullable=True)                   # Param 3c
    din = Column(String(20), nullable=True)                        # Param 3d
    uin = Column(String(20), nullable=True)                        # Param 3e
    nationality = Column(String(100), nullable=True)               # Param 4
    occupation = Column(String(255), nullable=True)                # Param 5
    # Param 6 = adverse media (live check)
    # Param 7 = PEP (live check)

    # Contact / Metadata
    email = Column(String(255), nullable=True)
    phone = Column(String(30), nullable=True)
    address = Column(Text, nullable=True)
    source = Column(String(50), default="CSV")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Customer {self.full_name} [{self.id}]>"