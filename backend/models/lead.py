from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal, List


LeadType = Literal["pre_approval", "test_drive", "contact", "availability"]
LeadStatus = Literal["new", "contacted", "qualified", "converted", "lost"]


class LeadNote(BaseModel):
    """Model for a lead note"""
    at: datetime
    by: str
    text: str


class NoteCreate(BaseModel):
    """Model for creating a new note"""
    text: str
    by: str = "admin"


class AssignmentUpdate(BaseModel):
    """Model for assigning a lead"""
    assigned_to: str


class LeadCreate(BaseModel):
    """Model for creating a new lead from any form"""
    lead_type: LeadType
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    message: Optional[str] = None
    
    # Vehicle info (optional)
    vehicle_id: Optional[str] = None
    vin: Optional[str] = None
    stock_number: Optional[str] = None
    year: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    trim: Optional[str] = None
    vehicle_summary: Optional[str] = None
    
    # Form-specific fields
    contact_preference: Optional[str] = None  # text | call | email
    preferred_date: Optional[str] = None  # Test drive date
    preferred_time: Optional[str] = None  # Test drive time
    
    # Tracking
    source_url: Optional[str] = None
    source: Optional[str] = None


class LeadOut(BaseModel):
    """Model for returning lead data"""
    id: str
    lead_type: str
    status: str
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    message: Optional[str] = None
    
    vehicle_id: Optional[str] = None
    vin: Optional[str] = None
    stock_number: Optional[str] = None
    year: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    trim: Optional[str] = None
    vehicle_summary: Optional[str] = None
    
    contact_preference: Optional[str] = None
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None
    
    source_url: Optional[str] = None
    source: Optional[str] = None
    
    # New fields for notes + assignment
    assigned_to: Optional[str] = None
    notes: List[LeadNote] = []
    last_contacted_at: Optional[datetime] = None
    
    created_at: datetime
    updated_at: datetime


class LeadStatusUpdate(BaseModel):
    """Model for updating lead status"""
    status: LeadStatus


# Legacy model for backward compatibility
class LegacyLeadCreate(BaseModel):
    """Legacy model for vehicle availability form"""
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
    """Legacy Lead model for backward compatibility"""
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
