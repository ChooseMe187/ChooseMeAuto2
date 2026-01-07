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
from services.image_service import (
    process_and_store_image,
    ImageValidationError,
    normalize_images_field,
    migrate_legacy_photo_urls,
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
    # Normalize images to consistent format
    images = normalize_images_field(doc)
    
    # Extract photo_urls for backward compatibility
    photo_urls = [img.get("url", img) if isinstance(img, dict) else img for img in images]
    
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
        # New images field with full metadata
        "images": images,
        # Legacy photo_urls for backward compatibility
        "photo_urls": photo_urls,
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
        "images": [],  # New consistent format
        "photo_urls": [],  # Legacy format for compatibility
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


# Upload Photos - NEW IMPLEMENTATION with Base64 storage
@router.post("/vehicles/{vehicle_id}/photos")
async def upload_vehicle_photos(
    vehicle_id: str,
    files: List[UploadFile] = File(...),
    _: bool = Depends(require_admin)
):
    """
    Upload photos for a vehicle.
    
    Images are processed, optimized, and stored as Base64 data URLs in MongoDB.
    This ensures persistence across deploys/restarts.
    
    Accepts: JPG, PNG, WebP (max 8MB each)
    """
    coll = get_vehicles_collection()
    
    try:
        vehicle = await coll.find_one({"_id": ObjectId(vehicle_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid vehicle ID")
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Get existing images
    existing_images = normalize_images_field(vehicle)
    
    uploaded_images = []
    errors = []
    
    for i, file in enumerate(files):
        try:
            # Read file content
            content = await file.read()
            
            # Determine if this should be primary (first image if none exist)
            is_primary = len(existing_images) == 0 and i == 0
            
            # Process and store image
            vehicle_image = await process_and_store_image(
                content=content,
                filename=file.filename,
                content_type=file.content_type,
                is_primary=is_primary,
                create_thumb=True,
            )
            
            uploaded_images.append(vehicle_image.to_dict())
            logger.info(f"Processed image: {file.filename} for vehicle {vehicle_id}")
            
        except ImageValidationError as e:
            errors.append({"filename": file.filename, "error": str(e)})
            logger.warning(f"Image validation failed: {file.filename} - {e}")
        except Exception as e:
            errors.append({"filename": file.filename, "error": f"Processing failed: {str(e)}"})
            logger.error(f"Image processing error: {file.filename} - {e}")
    
    if not uploaded_images and errors:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "All uploads failed",
                "errors": errors
            }
        )
    
    # Merge with existing images
    all_images = existing_images + uploaded_images
    
    # Extract URLs for legacy photo_urls field
    photo_urls = [img.get("url", "") for img in all_images]
    
    # Update vehicle
    await coll.update_one(
        {"_id": vehicle["_id"]},
        {"$set": {
            "images": all_images,
            "photo_urls": photo_urls,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    logger.info(f"Uploaded {len(uploaded_images)} photos for vehicle: {vehicle_id}")
    
    response = {
        "success": True,
        "uploaded_count": len(uploaded_images),
        "total_images": len(all_images),
        "images": all_images,
        "photo_urls": photo_urls,
    }
    
    if errors:
        response["errors"] = errors
        response["message"] = f"Uploaded {len(uploaded_images)} of {len(files)} files"
    
    return response


# Delete Photo
@router.delete("/vehicles/{vehicle_id}/photos/{photo_index}")
async def delete_vehicle_photo(
    vehicle_id: str,
    photo_index: int,
    _: bool = Depends(require_admin)
):
    """Delete a specific photo from a vehicle by index"""
    coll = get_vehicles_collection()
    
    try:
        vehicle = await coll.find_one({"_id": ObjectId(vehicle_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid vehicle ID")
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    images = normalize_images_field(vehicle)
    
    if photo_index < 0 or photo_index >= len(images):
        raise HTTPException(status_code=400, detail="Invalid photo index")
    
    # Remove the image
    removed_image = images.pop(photo_index)
    
    # If we removed the primary, make the first remaining image primary
    if removed_image.get("is_primary", False) and images:
        images[0]["is_primary"] = True
    
    # Extract URLs for legacy field
    photo_urls = [img.get("url", "") for img in images]
    
    # Update vehicle
    await coll.update_one(
        {"_id": vehicle["_id"]},
        {"$set": {
            "images": images,
            "photo_urls": photo_urls,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    logger.info(f"Deleted photo {photo_index} from vehicle: {vehicle_id}")
    
    return {
        "success": True,
        "message": "Photo deleted",
        "images": images,
        "photo_urls": photo_urls
    }


# Delete Photo by Upload ID
@router.delete("/vehicles/{vehicle_id}/photos/id/{upload_id}")
async def delete_vehicle_photo_by_id(
    vehicle_id: str,
    upload_id: str,
    _: bool = Depends(require_admin)
):
    """Delete a specific photo from a vehicle by upload_id"""
    coll = get_vehicles_collection()
    
    try:
        vehicle = await coll.find_one({"_id": ObjectId(vehicle_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid vehicle ID")
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    images = normalize_images_field(vehicle)
    
    # Find image by upload_id
    removed_index = None
    for i, img in enumerate(images):
        if img.get("upload_id") == upload_id:
            removed_index = i
            break
    
    if removed_index is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    removed_image = images.pop(removed_index)
    
    # If we removed the primary, make the first remaining image primary
    if removed_image.get("is_primary", False) and images:
        images[0]["is_primary"] = True
    
    photo_urls = [img.get("url", "") for img in images]
    
    await coll.update_one(
        {"_id": vehicle["_id"]},
        {"$set": {
            "images": images,
            "photo_urls": photo_urls,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    return {
        "success": True,
        "message": "Photo deleted",
        "images": images,
        "photo_urls": photo_urls
    }


# Set Primary Photo
@router.patch("/vehicles/{vehicle_id}/photos/{photo_index}/primary")
async def set_primary_photo(
    vehicle_id: str,
    photo_index: int,
    _: bool = Depends(require_admin)
):
    """Set a photo as the primary image"""
    coll = get_vehicles_collection()
    
    try:
        vehicle = await coll.find_one({"_id": ObjectId(vehicle_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid vehicle ID")
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    images = normalize_images_field(vehicle)
    
    if photo_index < 0 or photo_index >= len(images):
        raise HTTPException(status_code=400, detail="Invalid photo index")
    
    # Update primary flags
    for i, img in enumerate(images):
        img["is_primary"] = (i == photo_index)
    
    # Reorder so primary is first
    primary = images.pop(photo_index)
    images.insert(0, primary)
    
    photo_urls = [img.get("url", "") for img in images]
    
    await coll.update_one(
        {"_id": vehicle["_id"]},
        {"$set": {
            "images": images,
            "photo_urls": photo_urls,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    return {
        "success": True,
        "message": "Primary photo updated",
        "images": images,
        "photo_urls": photo_urls
    }


# Migration endpoint - migrate all existing records
@router.post("/migrate-images")
async def migrate_all_images(_: bool = Depends(require_admin)):
    """
    Migrate all vehicles from legacy photo_urls to new images[] schema.
    Safe to run multiple times (idempotent).
    """
    coll = get_vehicles_collection()
    
    # Find all vehicles
    cursor = coll.find({})
    vehicles = await cursor.to_list(None)
    
    migrated = 0
    skipped = 0
    
    for vehicle in vehicles:
        # Skip if already has images array with proper structure
        if vehicle.get("images") and isinstance(vehicle["images"], list):
            if vehicle["images"] and isinstance(vehicle["images"][0], dict):
                skipped += 1
                continue
        
        # Normalize images
        images = normalize_images_field(vehicle)
        photo_urls = [img.get("url", "") for img in images]
        
        # Update
        await coll.update_one(
            {"_id": vehicle["_id"]},
            {"$set": {
                "images": images,
                "photo_urls": photo_urls,
            }}
        )
        migrated += 1
    
    logger.info(f"Image migration complete: {migrated} migrated, {skipped} skipped")
    
    return {
        "success": True,
        "migrated": migrated,
        "skipped": skipped,
        "total": len(vehicles),
    }
