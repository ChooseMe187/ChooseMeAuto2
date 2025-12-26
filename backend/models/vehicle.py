from pydantic import BaseModel
from typing import Optional, List


class Vehicle(BaseModel):
    stock_id: str           # from "Stock #"
    vin: str
    year: int
    make: str
    model: str
    trim: str

    price: Optional[int] = None
    mileage: Optional[int] = None

    body_style: Optional[str] = None
    drivetrain: Optional[str] = None
    exterior_color: Optional[str] = None
    interior_color: Optional[str] = None
    
    # Computed condition field (New vs Used)
    condition: Optional[str] = None  # "New" or "Used"

    # Image fields
    image_url: Optional[str] = None      # Main Image URL
    image_urls: List[str] = []           # Additional images (2-5)
    photo_urls: List[str] = []           # Admin-uploaded photos
    
    # Document URLs
    carfax_url: Optional[str] = None
    window_sticker_url: Optional[str] = None
    
    # Call for Availability toggle
    call_for_availability_enabled: bool = False
