from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LeadCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=7, max_length=30)
    email: Optional[EmailStr] = None
    contact_preference: Optional[str] = Field(
        default="text", description="text | call | email"
    )
    message: Optional[str] = None

    stock_id: str
    vin: str
    vehicle_summary: str


class Lead(BaseModel):
    id: str
    created_at: datetime
    source: str = "choose-me-auto-website"
    name: str
    phone: str
    email: Optional[EmailStr] = None
    contact_preference: Optional[str] = "text"
    message: Optional[str] = None

    stock_id: str
    vin: str
    vehicle_summary: str
