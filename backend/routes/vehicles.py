from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from models.vehicle import Vehicle
from services.inventory_loader import list_vehicles as _list_vehicles, get_vehicle as _get_vehicle

router = APIRouter()


@router.get("/vehicles", response_model=List[Vehicle])
def get_vehicles(
    make: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    body_style: Optional[str] = Query(None),
    condition: Optional[str] = Query(None),
):
    """
    List vehicles with simple filters for SRP.

    Frontend-next can call:
    - /api/vehicles
    - /api/vehicles?make=Chevrolet&min_price=10000&max_price=40000
    - /api/vehicles?body_style=SUV
    - /api/vehicles?condition=Used
    """
    vehicles = _list_vehicles()

    def matches(v: Vehicle) -> bool:
        if make and v.make.lower() != make.lower():
            return False
        if model and v.model.lower() != model.lower():
            return False
        if body_style and (v.body_style or "").lower() != body_style.lower():
            return False
        if condition and (v.condition or "").lower() != condition.lower():
            return False
        if min_price is not None and (v.price or 0) < min_price:
            return False
        if max_price is not None and (v.price or 0) > max_price:
            return False
        return True

    return [v for v in vehicles if matches(v)]


@router.get("/vehicles/{stock_id}", response_model=Vehicle)
def get_vehicle_by_stock_id(stock_id: str):
    """
    Return a single vehicle for the VDP.

    Frontend-next should call:
    - /api/vehicles/{stock_id}
      matching /vehicle/[stock_id] route.
    """
    vehicle = _get_vehicle(stock_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle
