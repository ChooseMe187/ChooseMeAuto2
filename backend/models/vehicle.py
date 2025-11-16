from pydantic import BaseModel
from typing import Optional


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
