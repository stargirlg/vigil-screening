from datetime import date, datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class CustomerCreate(BaseModel):
    external_id: Optional[str] = None
    full_name: str
    dob: Optional[date] = None
    pan: Optional[str] = None
    aadhaar: Optional[str] = None
    passport: Optional[str] = None
    din: Optional[str] = None
    uin: Optional[str] = None
    nationality: Optional[str] = None
    occupation: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    source: str = "CSV"


class CustomerOut(BaseModel):
    id: UUID
    external_id: Optional[str] = None
    full_name: str
    dob: Optional[date] = None
    pan: Optional[str] = None
    nationality: Optional[str] = None
    occupation: Optional[str] = None
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CustomerScreenRequest(BaseModel):
    customer_id: UUID