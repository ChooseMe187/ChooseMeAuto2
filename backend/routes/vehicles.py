from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from models.vehicle import Vehicle

router = APIRouter()

# MongoDB connection - will be set in server.py
db = None

def set_db(database):
    global db
    db = database

def get_vehicles_collection():
    return db["admin_vehicles"]


def serialize_to_public_vehicle(doc) -> dict:
    """Convert MongoDB admin_vehicle document to public Vehicle format"""
    return {
        "stock_id": doc.get("stock_number") or str(doc.get("_id")),
        "id": str(doc.get("_id")),
        "vin": doc.get("vin", ""),
        "year": doc.get("year", 0),
        "make": doc.get("make", ""),
        "model": doc.get("model", ""),
        "trim": doc.get("trim", ""),
        "price": doc.get("price"),
        "mileage": doc.get("mileage"),
        "body_style": doc.get("body_style"),
        "drivetrain": doc.get("drivetrain"),
        "exterior_color": doc.get("exterior_color"),
        "interior_color": doc.get("interior_color"),
        "condition": doc.get("condition", "Used"),
        "image_url": doc.get("photo_urls", [])[0] if doc.get("photo_urls") else None,
        "image_urls": doc.get("photo_urls", [])[1:] if len(doc.get("photo_urls", [])) > 1 else [],
        "photo_urls": doc.get("photo_urls", []),
        # New fields
        "carfax_url": doc.get("carfax_url"),
        "window_sticker_url": doc.get("window_sticker_url"),
        "call_for_availability_enabled": doc.get("call_for_availability_enabled", False),
    }


@router.get("/vehicles")
async def get_vehicles(
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
    - /api/vehicles?condition=New
    """
    coll = get_vehicles_collection()
    
    # Build query filter
    query = {"is_active": True}
    
    if make:
        query["make"] = {"$regex": f"^{make}$", "$options": "i"}
    if model:
        query["model"] = {"$regex": f"^{model}$", "$options": "i"}
    if body_style:
        query["body_style"] = {"$regex": f"^{body_style}$", "$options": "i"}
    if condition:
        query["condition"] = {"$regex": f"^{condition}$", "$options": "i"}
    
    # Price filters
    if min_price is not None or max_price is not None:
        price_query = {}
        if min_price is not None:
            price_query["$gte"] = min_price
        if max_price is not None:
            price_query["$lte"] = max_price
        query["price"] = price_query
    
    # Projection for required fields only
    projection = {
        "_id": 1,
        "stock_number": 1,
        "vin": 1,
        "year": 1,
        "make": 1,
        "model": 1,
        "trim": 1,
        "price": 1,
        "mileage": 1,
        "body_style": 1,
        "drivetrain": 1,
        "exterior_color": 1,
        "interior_color": 1,
        "condition": 1,
        "photo_urls": 1,
        "carfax_url": 1,
        "window_sticker_url": 1,
        "call_for_availability_enabled": 1,
        "is_active": 1,
        "created_at": 1,
    }
    
    cursor = coll.find(query, projection).sort("created_at", -1).limit(200)
    vehicles = await cursor.to_list(200)
    
    return [serialize_to_public_vehicle(v) for v in vehicles]


@router.get("/vehicles/{stock_id}")
async def get_vehicle_by_stock_id(stock_id: str):
    """
    Return a single vehicle for the VDP.

    Frontend-next should call:
    - /api/vehicles/{stock_id}
      matching /vehicle/[stock_id] route.
    """
    coll = get_vehicles_collection()
    
    # Try to find by stock_number first
    vehicle = await coll.find_one({"stock_number": stock_id, "is_active": True})
    
    # If not found, try by MongoDB _id
    if not vehicle:
        from bson import ObjectId
        try:
            vehicle = await coll.find_one({"_id": ObjectId(stock_id), "is_active": True})
        except:
            pass
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return serialize_to_public_vehicle(vehicle)
