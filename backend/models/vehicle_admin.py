from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class VehicleCreate(BaseModel):
    """Model for creating a new vehicle"""
    vin: str
    stock_number: Optional[str] = None
    
    year: int
    make: str
    model: str
    trim: Optional[str] = None
    
    price: Optional[float] = None
    mileage: Optional[int] = None
    
    condition: Optional[str] = "Used"  # "New" or "Used"
    body_style: Optional[str] = None
    exterior_color: Optional[str] = None
    interior_color: Optional[str] = None
    transmission: Optional[str] = None
    drivetrain: Optional[str] = None
    engine: Optional[str] = None
    
    # Document URLs
    carfax_url: Optional[str] = None
    window_sticker_url: Optional[str] = None
    
    # Call for Availability toggle
    call_for_availability_enabled: bool = False
    
    is_featured: bool = False
    is_active: bool = True


class VehicleUpdate(BaseModel):
    """Model for updating a vehicle (all fields optional)"""
    vin: Optional[str] = None
    stock_number: Optional[str] = None
    
    year: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    trim: Optional[str] = None
    
    price: Optional[float] = None
    mileage: Optional[int] = None
    
    condition: Optional[str] = None
    body_style: Optional[str] = None
    exterior_color: Optional[str] = None
    interior_color: Optional[str] = None
    transmission: Optional[str] = None
    drivetrain: Optional[str] = None
    engine: Optional[str] = None
    
    # Document URLs
    carfax_url: Optional[str] = None
    window_sticker_url: Optional[str] = None
    
    # Call for Availability toggle
    call_for_availability_enabled: Optional[bool] = None
    
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None


class VehicleInDB(BaseModel):
    """Vehicle model as stored in database"""
    id: str
    vin: str
    stock_number: Optional[str] = None
    
    year: int
    make: str
    model: str
    trim: Optional[str] = None
    
    price: Optional[float] = None
    mileage: Optional[int] = None
    
    condition: Optional[str] = "Used"
    body_style: Optional[str] = None
    exterior_color: Optional[str] = None
    interior_color: Optional[str] = None
    transmission: Optional[str] = None
    drivetrain: Optional[str] = None
    engine: Optional[str] = None
    
    # Document URLs
    carfax_url: Optional[str] = None
    window_sticker_url: Optional[str] = None
    
    # Call for Availability toggle
    call_for_availability_enabled: bool = False
    
    is_featured: bool = False
    is_active: bool = True
    
    photo_urls: List[str] = []
    created_at: datetime
    updated_at: datetime


class AdminLoginRequest(BaseModel):
    password: str


class AdminLoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    message: str
