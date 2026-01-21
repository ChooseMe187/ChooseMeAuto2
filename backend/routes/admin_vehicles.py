from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request, Query
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
import os
import uuid
import logging
import io

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
from services.csv_import_service import (
    process_csv_import,
    generate_csv_template,
    CSVValidationError,
    MAX_CSV_SIZE_MB,
)

logger = logging.getLogger(__name__)

# Custom response class that adds noindex header to all admin responses
class AdminJSONResponse(JSONResponse):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers["X-Robots-Tag"] = "noindex, nofollow"

router = APIRouter(
    prefix="/api/admin", 
    tags=["admin-vehicles"],
    default_response_class=AdminJSONResponse
)

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
async def admin_login(login_request: AdminLoginRequest, request: Request):
    """Admin login endpoint with rate limiting"""
    result = await verify_admin_login(login_request.password, request)
    
    if result["success"]:
        return AdminLoginResponse(
            success=True,
            token=ADMIN_TOKEN,
            message=result["message"]
        )
    else:
        return AdminLoginResponse(
            success=False,
            token=None,
            message=result["message"]
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


# CSV Template Download (must be before {vehicle_id} route)
@router.get("/vehicles/csv-template")
async def download_csv_template(_: bool = Depends(require_admin)):
    """
    Download a CSV template with headers and a sample row.
    
    Use this template to prepare your vehicle inventory for import.
    """
    template_content = generate_csv_template()
    
    return StreamingResponse(
        io.BytesIO(template_content.encode('utf-8')),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=vehicle_import_template.csv",
            "X-Robots-Tag": "noindex, nofollow"
        }
    )


# ============================================================
# DEBUG & SYNC ENDPOINTS
# ============================================================

@router.get("/vehicles/debug-counts")
async def debug_vehicle_counts(_: bool = Depends(require_admin)):
    """
    Debug endpoint to diagnose vehicle count mismatches between collections.
    
    Returns database info, collection names, counts, and sample document fields.
    Use this to identify why admin panel might show different vehicles than public API.
    """
    # Get all collections
    collections = await db.list_collection_names()
    
    # Count documents in potential vehicle collections
    counts = {}
    sample_fields = {}
    
    # The EXACT filter, sort, and limit used in list_vehicles endpoint
    admin_query_config = {
        "filter": {},  # No filter applied
        "sort": {"created_at": -1},
        "limit": 500,
        "collection": "admin_vehicles",
    }
    
    # Check admin_vehicles (what admin panel uses)
    admin_coll = db["admin_vehicles"]
    counts["admin_vehicles_total"] = await admin_coll.count_documents({})
    counts["admin_vehicles_active"] = await admin_coll.count_documents({"is_active": {"$ne": False}})
    
    # Apply the EXACT same query as list_vehicles to show what admin panel sees
    admin_cursor = admin_coll.find(
        admin_query_config["filter"]
    ).sort(
        list(admin_query_config["sort"].items())
    ).limit(admin_query_config["limit"])
    admin_results = await admin_cursor.to_list(admin_query_config["limit"])
    counts["admin_vehicles_query_result"] = len(admin_results)
    
    # Get sample document fields from admin_vehicles
    sample_admin = await admin_coll.find_one({})
    sample_fields["admin_vehicles"] = list((sample_admin or {}).keys()) if sample_admin else []
    
    # Check if there's a separate 'vehicles' collection
    if "vehicles" in collections:
        vehicles_coll = db["vehicles"]
        counts["vehicles_total"] = await vehicles_coll.count_documents({})
        counts["vehicles_active"] = await vehicles_coll.count_documents({"is_active": {"$ne": False}})
        sample_public = await vehicles_coll.find_one({})
        sample_fields["vehicles"] = list((sample_public or {}).keys()) if sample_public else []
    
    # Check for any other potential vehicle collections
    for coll_name in collections:
        if "vehicle" in coll_name.lower() and coll_name not in ["admin_vehicles", "vehicles"]:
            counts[f"{coll_name}_total"] = await db[coll_name].count_documents({})
    
    return {
        "db_name": db.name,
        "collections": collections,
        "counts": counts,
        "admin_query": {
            "description": "Exact query used by GET /api/admin/vehicles",
            "collection": admin_query_config["collection"],
            "filter": admin_query_config["filter"],
            "sort": admin_query_config["sort"],
            "limit": admin_query_config["limit"],
            "result_count": counts["admin_vehicles_query_result"],
        },
        "sample_doc_fields": sample_fields,
        "diagnosis": {
            "admin_vehicles_has_data": counts.get("admin_vehicles_total", 0) > 0,
            "vehicles_collection_exists": "vehicles" in collections,
            "potential_collection_mismatch": (
                counts.get("vehicles_total", 0) > 0 and 
                counts.get("admin_vehicles_total", 0) != counts.get("vehicles_total", 0)
            ) if "vehicles" in collections else False,
            "query_returns_all": counts["admin_vehicles_query_result"] == counts["admin_vehicles_total"],
        }
    }


# Rate limiting for sync (simple in-memory tracker)
sync_last_run = {}
SYNC_COOLDOWN_SECONDS = 60  # 1 minute cooldown

@router.post("/vehicles/sync")
async def sync_vehicles_to_admin(
    request: Request,
    source_collection: str = Query(default="vehicles", description="Source collection name"),
    _: bool = Depends(require_admin)
):
    """
    Sync vehicles from a source collection to admin_vehicles.
    
    This endpoint:
    1. Reads from the specified source collection
    2. Normalizes the data to admin format
    3. Upserts into admin_vehicles by VIN
    
    Use this to fix mismatches between public API and admin panel.
    
    **Rate limited**: Can only be run once per minute.
    """
    # Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    import time
    current_time = time.time()
    last_run = sync_last_run.get(client_ip, 0)
    
    if (current_time - last_run) < SYNC_COOLDOWN_SECONDS:
        remaining = int(SYNC_COOLDOWN_SECONDS - (current_time - last_run))
        raise HTTPException(
            status_code=429,
            detail=f"Sync can only be run once per minute. Please wait {remaining} seconds."
        )
    
    # Check if source collection exists
    collections = await db.list_collection_names()
    if source_collection not in collections:
        raise HTTPException(
            status_code=400,
            detail=f"Source collection '{source_collection}' not found. Available: {collections}"
        )
    
    source = db[source_collection]
    target = db["admin_vehicles"]
    
    inserted = 0
    updated = 0
    skipped = 0
    errors = []
    
    # Get all documents from source
    cursor = source.find({})
    docs = await cursor.to_list(length=1000)
    
    logger.info(f"Sync starting: {len(docs)} documents from '{source_collection}'")
    
    for doc in docs:
        try:
            # Get VIN (try different field names)
            vin = doc.get("vin") or doc.get("VIN") or doc.get("Vin")
            
            if not vin:
                skipped += 1
                continue
            
            # Normalize the document
            normalized = normalize_vehicle_for_admin(doc)
            normalized["vin"] = vin
            normalized["updated_at"] = datetime.now(timezone.utc)
            
            # Upsert by VIN
            result = await target.update_one(
                {"vin": vin},
                {
                    "$set": normalized,
                    "$setOnInsert": {"created_at": datetime.now(timezone.utc)}
                },
                upsert=True
            )
            
            if result.upserted_id:
                inserted += 1
            elif result.modified_count:
                updated += 1
                
        except Exception as e:
            logger.error(f"Sync error for doc: {e}")
            errors.append(str(e)[:100])
            skipped += 1
    
    # Update rate limit tracker
    sync_last_run[client_ip] = current_time
    
    # Get final count
    final_count = await target.count_documents({})
    
    logger.info(f"Sync complete: {inserted} inserted, {updated} updated, {skipped} skipped")
    
    return {
        "success": True,
        "source_collection": source_collection,
        "target_collection": "admin_vehicles",
        "results": {
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped,
            "errors": errors[:5] if errors else [],
        },
        "final_admin_count": final_count,
    }


def normalize_vehicle_for_admin(doc: dict) -> dict:
    """
    Normalize a vehicle document from any source to admin_vehicles format.
    
    Handles common field name variations and data type differences.
    """
    # Price normalization
    price = doc.get("price") or doc.get("internetPrice") or doc.get("salePrice") or doc.get("Price")
    if price is not None:
        try:
            if isinstance(price, str):
                price = float(price.replace(",", "").replace("$", "").strip())
            price = float(price)
        except (ValueError, TypeError):
            price = None
    
    # Mileage normalization
    mileage = doc.get("mileage") or doc.get("odometer") or doc.get("Mileage")
    if mileage is not None:
        try:
            if isinstance(mileage, str):
                mileage = int(mileage.replace(",", "").strip())
            mileage = int(mileage)
        except (ValueError, TypeError):
            mileage = None
    
    # Year normalization
    year = doc.get("year") or doc.get("Year")
    if year is not None:
        try:
            year = int(year)
        except (ValueError, TypeError):
            year = None
    
    # Images normalization
    images = doc.get("images") or doc.get("photos") or doc.get("image_urls") or []
    if isinstance(images, str):
        images = [{"url": images, "is_primary": True}]
    elif isinstance(images, list):
        # Normalize to [{url, is_primary}] format
        normalized_images = []
        for i, img in enumerate(images):
            if isinstance(img, str):
                normalized_images.append({"url": img, "is_primary": i == 0})
            elif isinstance(img, dict):
                normalized_images.append(img)
        images = normalized_images
    
    # Handle primary_image_url separately
    primary_url = doc.get("primary_image_url") or doc.get("image_url")
    if primary_url and not images:
        images = [{"url": primary_url, "is_primary": True}]
    
    return {
        "stock_number": doc.get("stock_number") or doc.get("stock") or doc.get("stockNumber") or doc.get("stock_id"),
        "year": year,
        "make": (doc.get("make") or doc.get("Make") or "").strip(),
        "model": (doc.get("model") or doc.get("Model") or "").strip(),
        "trim": (doc.get("trim") or doc.get("Trim") or "").strip(),
        "mileage": mileage,
        "price": price,
        "condition": doc.get("condition") or doc.get("Condition") or "Used",
        "body_style": doc.get("body_style") or doc.get("bodyStyle") or doc.get("body") or "",
        "exterior_color": doc.get("exterior_color") or doc.get("exteriorColor") or doc.get("color") or "",
        "interior_color": doc.get("interior_color") or doc.get("interiorColor") or "",
        "transmission": doc.get("transmission") or doc.get("Transmission") or "",
        "drivetrain": doc.get("drivetrain") or doc.get("driveType") or "",
        "fuel_type": doc.get("fuel_type") or doc.get("fuelType") or "",
        "engine": doc.get("engine") or doc.get("Engine") or "",
        "carfax_url": doc.get("carfax_url") or doc.get("carfaxUrl") or "",
        "window_sticker_url": doc.get("window_sticker_url") or doc.get("windowStickerUrl") or "",
        "images": images,
        "is_active": doc.get("is_active", True),
        "is_featured_homepage": doc.get("is_featured_homepage", False),
        "featured_rank": doc.get("featured_rank"),
        "call_for_availability_enabled": doc.get("call_for_availability_enabled", False),
        "sync_source": "admin_sync",
    }


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
MAX_IMAGES_PER_VEHICLE = int(os.environ.get("MAX_IMAGES_PER_VEHICLE", "12"))

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
    
    Limits:
    - Max 12 images per vehicle (configurable)
    - Max 8MB per image
    - Accepts: JPG, PNG, WebP
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
    current_count = len(existing_images)
    
    # Check if adding these would exceed the limit
    if current_count + len(files) > MAX_IMAGES_PER_VEHICLE:
        remaining_slots = MAX_IMAGES_PER_VEHICLE - current_count
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Image limit exceeded. Maximum {MAX_IMAGES_PER_VEHICLE} images per vehicle.",
                "current_count": current_count,
                "remaining_slots": remaining_slots,
                "attempted_upload": len(files)
            }
        )
    
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


# ============================================================
# CSV IMPORT ENDPOINTS
# ============================================================

# Rate limiting for CSV imports (simple in-memory tracker)
csv_import_tracker = {}
CSV_IMPORT_COOLDOWN_SECONDS = 30  # Minimum time between imports

@router.post("/vehicles/import-csv")
async def import_vehicles_csv(
    request: Request,
    file: UploadFile = File(...),
    dry_run: bool = Query(default=True, description="Preview only, no database changes"),
    _: bool = Depends(require_admin)
):
    """
    Import vehicles from CSV file with upsert by VIN.
    
    - **dry_run=true**: Preview import (default) - validates and shows what would happen
    - **dry_run=false**: Execute import - creates/updates vehicles in database
    
    VIN is the unique identifier. Existing VINs will be updated, new VINs will be created.
    
    Required CSV columns: vin, year, make, model, price
    """
    # Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    last_import = csv_import_tracker.get(client_ip, 0)
    current_time = datetime.now(timezone.utc).timestamp()
    
    if not dry_run and (current_time - last_import) < CSV_IMPORT_COOLDOWN_SECONDS:
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {CSV_IMPORT_COOLDOWN_SECONDS} seconds between imports"
        )
    
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"CSV upload read error: {e}")
        raise HTTPException(status_code=400, detail="Failed to read uploaded file")
    
    # Check file size
    if len(content) > MAX_CSV_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size is {MAX_CSV_SIZE_MB}MB"
        )
    
    # Process import
    try:
        result = await process_csv_import(content, db, dry_run=dry_run)
        
        # Update rate limit tracker on successful non-dry-run import
        if not dry_run and result['success']:
            csv_import_tracker[client_ip] = current_time
            logger.info(f"CSV Import completed: {result['counts']}")
        
        return result
        
    except CSVValidationError as e:
        logger.warning(f"CSV validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"CSV import error: {e}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
