from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
import os
import uuid
import logging

from motor.motor_asyncio import AsyncIOMotorClient

from auth import require_admin, verify_admin_login, ADMIN_TOKEN
from models.vehicle_admin import (
    VehicleCreate, 
    VehicleUpdate, 
    VehicleInDB, 
    AdminLoginRequest, 
    AdminLoginResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin-vehicles"])

# MongoDB connection - will be set in server.py
db = None

def set_db(database):
    global db
    db = database

def get_vehicles_collection():
    return db["admin_vehicles"]


def serialize_vehicle(doc) -> dict:
    """Convert MongoDB document to VehicleInDB format"""
    return {
        "id": str(doc["_id"]),
        "vin": doc.get("vin", ""),
        "stock_number": doc.get("stock_number"),
        "year": doc.get("year", 0),
        "make": doc.get("make", ""),
        "model": doc.get("model", ""),
        "trim": doc.get("trim"),
        "price": doc.get("price"),
        "mileage": doc.get("mileage"),
        "condition": doc.get("condition", "Used"),
        "body_style": doc.get("body_style"),
        "exterior_color": doc.get("exterior_color"),
        "interior_color": doc.get("interior_color"),
        "transmission": doc.get("transmission"),
        "drivetrain": doc.get("drivetrain"),
        "engine": doc.get("engine"),
        "carfax_url": doc.get("carfax_url"),
        "window_sticker_url": doc.get("window_sticker_url"),
        "call_for_availability_enabled": doc.get("call_for_availability_enabled", False),
        "is_featured": doc.get("is_featured", False),
        "is_featured_homepage": doc.get("is_featured_homepage", False),
        "featured_rank": doc.get("featured_rank"),
        "is_active": doc.get("is_active", True),
        "photo_urls": doc.get("photo_urls", []),
        "created_at": doc.get("created_at", datetime.now(timezone.utc)),
        "updated_at": doc.get("updated_at", datetime.now(timezone.utc)),
    }


# Admin Login
@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest):
    """Admin login endpoint"""
    is_valid = await verify_admin_login(request.password)
    if is_valid:
        return AdminLoginResponse(
            success=True,
            token=ADMIN_TOKEN,
            message="Login successful"
        )
    return AdminLoginResponse(
        success=False,
        token=None,
        message="Invalid password"
    )


# Create Vehicle
@router.post("/vehicles", response_model=VehicleInDB, status_code=status.HTTP_201_CREATED)
async def create_vehicle(payload: VehicleCreate, _: bool = Depends(require_admin)):
    """Create a new vehicle"""
    coll = get_vehicles_collection()
    
    # Check for duplicate VIN
    existing = await coll.find_one({"vin": payload.vin})
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Vehicle with this VIN already exists."
        )
    
    now = datetime.now(timezone.utc)
    
    # Generate stock number if not provided
    stock_number = payload.stock_number
    if not stock_number:
        # Generate a unique stock number like "CMA12345"
        stock_number = f"CMA{uuid.uuid4().hex[:6].upper()}"
    
    doc = {
        **payload.model_dump(),
        "stock_number": stock_number,
        "photo_urls": [],
        "created_at": now,
        "updated_at": now,
    }
    
    result = await coll.insert_one(doc)
    doc["_id"] = result.inserted_id
    
    logger.info(f"Created vehicle: {payload.year} {payload.make} {payload.model} (VIN: {payload.vin})")
    return serialize_vehicle(doc)


# List All Vehicles
@router.get("/vehicles", response_model=List[VehicleInDB])
async def list_vehicles(_: bool = Depends(require_admin)):
    """List all vehicles in admin inventory"""
    coll = get_vehicles_collection()
    cursor = coll.find({}).sort("created_at", -1).limit(500)
    vehicles = await cursor.to_list(500)
    return [serialize_vehicle(v) for v in vehicles]


# Get Single Vehicle
@router.get("/vehicles/{vehicle_id}", response_model=VehicleInDB)
async def get_vehicle(vehicle_id: str, _: bool = Depends(require_admin)):
    """Get a single vehicle by ID"""
    coll = get_vehicles_collection()
    
    try:
        vehicle = await coll.find_one({"_id": ObjectId(vehicle_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid vehicle ID")
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return serialize_vehicle(vehicle)


# Update Vehicle
@router.patch("/vehicles/{vehicle_id}", response_model=VehicleInDB)
async def update_vehicle(
    vehicle_id: str, 
    payload: VehicleUpdate, 
    _: bool = Depends(require_admin)
):
    """Update a vehicle"""
    coll = get_vehicles_collection()
    
    try:
        vehicle = await coll.find_one({"_id": ObjectId(vehicle_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid vehicle ID")
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Only update fields that are provided
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await coll.update_one(
        {"_id": ObjectId(vehicle_id)},
        {"$set": update_data}
    )
    
    updated = await coll.find_one({"_id": ObjectId(vehicle_id)})
    logger.info(f"Updated vehicle: {vehicle_id}")
    return serialize_vehicle(updated)


# Delete Vehicle
@router.delete("/vehicles/{vehicle_id}")
async def delete_vehicle(vehicle_id: str, _: bool = Depends(require_admin)):
    """Delete a vehicle"""
    coll = get_vehicles_collection()
    
    try:
        result = await coll.delete_one({"_id": ObjectId(vehicle_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid vehicle ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    logger.info(f"Deleted vehicle: {vehicle_id}")
    return {"message": "Vehicle deleted successfully"}


# Upload Photos
UPLOAD_ROOT = "/app/frontend/public/admin-vehicles"

@router.post("/vehicles/{vehicle_id}/photos")
async def upload_vehicle_photos(
    vehicle_id: str,
    files: List[UploadFile] = File(...),
    _: bool = Depends(require_admin)
):
    """Upload photos for a vehicle"""
    coll = get_vehicles_collection()
    
    try:
        vehicle = await coll.find_one({"_id": ObjectId(vehicle_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid vehicle ID")
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Create upload directory
    os.makedirs(UPLOAD_ROOT, exist_ok=True)
    vehicle_folder = os.path.join(UPLOAD_ROOT, vehicle_id)
    os.makedirs(vehicle_folder, exist_ok=True)
    
    photo_urls = vehicle.get("photo_urls", [])
    
    for file in files:
        # Get file extension
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(vehicle_folder, filename)
        
        # Save file
        contents = await file.read()
        with open(filepath, "wb") as f:
            f.write(contents)
        
        # Store relative URL for frontend
        url = f"/admin-vehicles/{vehicle_id}/{filename}"
        photo_urls.append(url)
    
    # Update vehicle with new photo URLs
    await coll.update_one(
        {"_id": vehicle["_id"]},
        {"$set": {"photo_urls": photo_urls, "updated_at": datetime.now(timezone.utc)}}
    )
    
    logger.info(f"Uploaded {len(files)} photos for vehicle: {vehicle_id}")
    return {"photo_count": len(photo_urls), "photo_urls": photo_urls}


# Delete Photo
@router.delete("/vehicles/{vehicle_id}/photos/{photo_index}")
async def delete_vehicle_photo(
    vehicle_id: str,
    photo_index: int,
    _: bool = Depends(require_admin)
):
    """Delete a specific photo from a vehicle"""
    coll = get_vehicles_collection()
    
    try:
        vehicle = await coll.find_one({"_id": ObjectId(vehicle_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid vehicle ID")
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    photo_urls = vehicle.get("photo_urls", [])
    
    if photo_index < 0 or photo_index >= len(photo_urls):
        raise HTTPException(status_code=400, detail="Invalid photo index")
    
    # Remove from list
    removed_url = photo_urls.pop(photo_index)
    
    # Try to delete file from disk
    try:
        filepath = os.path.join("/app/frontend/public", removed_url.lstrip("/"))
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        logger.warning(f"Could not delete photo file: {e}")
    
    # Update vehicle
    await coll.update_one(
        {"_id": vehicle["_id"]},
        {"$set": {"photo_urls": photo_urls, "updated_at": datetime.now(timezone.utc)}}
    )
    
    return {"message": "Photo deleted", "photo_urls": photo_urls}
