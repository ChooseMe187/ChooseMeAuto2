from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from models.vehicle import Vehicle
from services.image_service import normalize_images_field

router = APIRouter()

# MongoDB connection - will be set in server.py
db = None

def set_db(database):
    global db
    db = database

def get_vehicles_collection():
    return db["admin_vehicles"]


def serialize_to_public_vehicle_list(doc) -> dict:
    """
    Lightweight serializer for vehicle lists (SRP, Featured, Homepage).
    Returns thumbnail URLs only to improve page load speed.
    """
    images = normalize_images_field(doc)
    
    # Get primary thumbnail (first image or first with is_primary=True)
    primary_url = None
    for img in images:
        if isinstance(img, dict):
            # Prefer thumbnail_url for list views (smaller payload)
            thumb = img.get("thumbnail_url")
            url = img.get("url", "")
            if img.get("is_primary"):
                primary_url = thumb or url
                break
            if not primary_url:
                primary_url = thumb or url
        else:
            if not primary_url:
                primary_url = img
    
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
        "condition": doc.get("condition", "Used"),
        # Only primary thumbnail for lists (faster loading)
        "primary_image_url": primary_url,
        "image_url": primary_url,
        # Featured flags
        "is_featured_homepage": doc.get("is_featured_homepage", False),
        "featured_rank": doc.get("featured_rank"),
    }


def serialize_to_public_vehicle_detail(doc) -> dict:
    """
    Full serializer for vehicle detail pages (VDP).
    Returns all images with full URLs for gallery view.
    """
    images = normalize_images_field(doc)
    
    # Get primary and other images
    primary_url = None
    other_urls = []
    all_urls = []
    
    for img in images:
        url = img.get("url", "") if isinstance(img, dict) else img
        all_urls.append(url)
        
        if isinstance(img, dict) and img.get("is_primary"):
            primary_url = url
        elif not primary_url:
            primary_url = url
        else:
            other_urls.append(url)
    
    # Ensure primary is first
    photo_urls = [primary_url] + other_urls if primary_url else other_urls
    
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
        # Full image URLs for detail view
        "image_url": primary_url,
        "image_urls": other_urls,
        "photo_urls": photo_urls,
        "primary_image_url": primary_url,
        "images": images,
        # Document & CTA fields
        "carfax_url": doc.get("carfax_url"),
        "window_sticker_url": doc.get("window_sticker_url"),
        "call_for_availability_enabled": doc.get("call_for_availability_enabled", False),
        # Featured flags
        "is_featured_homepage": doc.get("is_featured_homepage", False),
        "featured_rank": doc.get("featured_rank"),
    }


# Legacy function for backward compatibility
def serialize_to_public_vehicle(doc) -> dict:
    """Alias for detail serializer"""
    return serialize_to_public_vehicle_detail(doc)


@router.get("/vehicles/featured")
async def get_featured_vehicles(limit: int = Query(8, ge=1, le=20)):
    """
    Get featured vehicles for homepage display.
    Returns lightweight data with thumbnails only for fast loading.
    """
    coll = get_vehicles_collection()
    
    query = {
        "is_active": True,
        "is_featured_homepage": True,
    }
    
    # Only fetch fields needed for list view
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
        "condition": 1,
        "images": 1,  # Need images for thumbnail extraction
        "is_featured_homepage": 1,
        "featured_rank": 1,
    }
    
    cursor = coll.find(query, projection).sort([
        ("featured_rank", 1),
        ("created_at", -1)
    ]).limit(limit)
    
    vehicles = await cursor.to_list(limit)
    
    # Use lightweight serializer for list view
    return [serialize_to_public_vehicle_list(v) for v in vehicles]


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
    
    # Projection for list view (lightweight, thumbnails only)
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
        "condition": 1,
        "images": 1,  # For thumbnail extraction
        "is_featured_homepage": 1,
    }
    
    cursor = coll.find(query, projection).sort("created_at", -1).limit(200)
    vehicles = await cursor.to_list(200)
    
    # Use lightweight serializer for faster list loading
    return [serialize_to_public_vehicle_list(v) for v in vehicles]


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
