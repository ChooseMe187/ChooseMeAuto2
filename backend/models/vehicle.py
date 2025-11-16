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

    # Image fields
    image_url: Optional[str] = None      # Main Image URL
    image_urls: List[str] = []            # Additional images (2-5)
