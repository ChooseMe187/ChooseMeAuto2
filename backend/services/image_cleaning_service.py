"""
Image Cleaning Service

Removes dealership branding/watermarks from vehicle photos.
Creates multiple derivatives: thumb, display, full, clean.

Supports:
- Bottom strip cropping (most common for dealer watermarks)
- Top strip cropping
- Corner watermark cropping
- Custom crop regions

Storage: Processed images are Base64 encoded and stored in MongoDB.
For production scale, switch to S3/R2 storage.
"""
import base64
import logging
from io import BytesIO
from typing import Dict, List, Optional, Tuple
from PIL import Image
import os
import httpx
import asyncio

logger = logging.getLogger(__name__)

# Configuration
CROP_BOTTOM_PIXELS = int(os.environ.get("CROP_BOTTOM_PIXELS", "60"))  # Default: crop 60px from bottom
CROP_TOP_PIXELS = int(os.environ.get("CROP_TOP_PIXELS", "0"))
IMAGE_QUALITY_FULL = int(os.environ.get("IMAGE_QUALITY_FULL", "92"))
IMAGE_QUALITY_DISPLAY = int(os.environ.get("IMAGE_QUALITY_DISPLAY", "88"))
IMAGE_QUALITY_THUMB = int(os.environ.get("IMAGE_QUALITY_THUMB", "80"))

# Output dimensions
DISPLAY_MAX_WIDTH = 1200
DISPLAY_MAX_HEIGHT = 900
THUMB_WIDTH = 300
THUMB_HEIGHT = 225
FULL_MAX_WIDTH = 1920
FULL_MAX_HEIGHT = 1440


class ImageCleaningError(Exception):
    """Raised when image cleaning fails"""
    pass


def crop_branding(img: Image.Image, 
                  crop_bottom: int = CROP_BOTTOM_PIXELS,
                  crop_top: int = CROP_TOP_PIXELS,
                  crop_left: int = 0,
                  crop_right: int = 0) -> Image.Image:
    """
    Crop branding areas from image.
    
    Args:
        img: PIL Image
        crop_bottom: Pixels to remove from bottom (common for dealer banners)
        crop_top: Pixels to remove from top
        crop_left: Pixels to remove from left
        crop_right: Pixels to remove from right
    
    Returns:
        Cropped PIL Image
    """
    width, height = img.size
    
    # Calculate crop box (left, upper, right, lower)
    left = crop_left
    upper = crop_top
    right = width - crop_right
    lower = height - crop_bottom
    
    # Validate crop dimensions
    if right <= left or lower <= upper:
        logger.warning(f"Invalid crop dimensions for {width}x{height} image, skipping crop")
        return img
    
    # Ensure we don't crop too much (max 20% from any side)
    max_vertical_crop = int(height * 0.20)
    max_horizontal_crop = int(width * 0.20)
    
    if crop_bottom > max_vertical_crop:
        crop_bottom = max_vertical_crop
        lower = height - crop_bottom
    
    if crop_top > max_vertical_crop:
        crop_top = max_vertical_crop
        upper = crop_top
    
    return img.crop((left, upper, right, lower))


def smart_resize(img: Image.Image, max_width: int, max_height: int) -> Image.Image:
    """Resize image while preserving aspect ratio."""
    if img.width <= max_width and img.height <= max_height:
        return img
    
    ratio = min(max_width / img.width, max_height / img.height)
    new_size = (int(img.width * ratio), int(img.height * ratio))
    
    return img.resize(new_size, Image.Resampling.LANCZOS)


def create_thumbnail(img: Image.Image, width: int = THUMB_WIDTH, height: int = THUMB_HEIGHT) -> Image.Image:
    """Create a thumbnail with exact dimensions (may crop to fit)."""
    # Calculate aspect ratios
    target_ratio = width / height
    img_ratio = img.width / img.height
    
    if img_ratio > target_ratio:
        # Image is wider - crop sides
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        img = img.crop((left, 0, left + new_width, img.height))
    else:
        # Image is taller - crop top/bottom
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        img = img.crop((0, top, img.width, top + new_height))
    
    return img.resize((width, height), Image.Resampling.LANCZOS)


def convert_to_rgb(img: Image.Image) -> Image.Image:
    """Convert image to RGB, handling transparency."""
    if img.mode == 'RGB':
        return img
    
    if img.mode in ('RGBA', 'P', 'LA'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'RGBA':
            background.paste(img, mask=img.split()[3])
        elif img.mode == 'LA':
            background.paste(img, mask=img.split()[1])
        else:
            img_rgba = img.convert('RGBA')
            background.paste(img_rgba, mask=img_rgba.split()[3])
        return background
    
    return img.convert('RGB')


def correct_exif_orientation(img: Image.Image) -> Image.Image:
    """Auto-correct image orientation from EXIF data."""
    try:
        from PIL import ExifTags
        exif = img._getexif()
        if exif is None:
            return img
        
        orientation_key = None
        for key, value in ExifTags.TAGS.items():
            if value == 'Orientation':
                orientation_key = key
                break
        
        if orientation_key is None or orientation_key not in exif:
            return img
        
        orientation = exif[orientation_key]
        
        if orientation == 2:
            img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            img = img.rotate(180, expand=True)
        elif orientation == 4:
            img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            img = img.rotate(90, expand=True)
        elif orientation == 6:
            img = img.rotate(-90, expand=True)
        elif orientation == 7:
            img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            img = img.rotate(-90, expand=True)
        elif orientation == 8:
            img = img.rotate(90, expand=True)
        
        return img
    except (AttributeError, KeyError, TypeError):
        return img


def image_to_data_url(img: Image.Image, quality: int = 85) -> str:
    """Convert PIL Image to Base64 data URL."""
    buffer = BytesIO()
    img.save(buffer, format='WEBP', quality=quality, method=6, optimize=True)
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode('utf-8')
    return f"data:image/webp;base64,{b64}"


async def download_image(url: str, timeout: int = 30) -> bytes:
    """Download image from URL."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=timeout, follow_redirects=True)
        response.raise_for_status()
        return response.content


def process_image_for_clean_storage(
    content: bytes,
    crop_bottom: int = CROP_BOTTOM_PIXELS,
    crop_top: int = CROP_TOP_PIXELS,
    generate_derivatives: bool = True
) -> Dict[str, str]:
    """
    Process an image: correct orientation, crop branding, generate derivatives.
    
    Args:
        content: Raw image bytes
        crop_bottom: Pixels to crop from bottom
        crop_top: Pixels to crop from top
        generate_derivatives: Whether to generate thumb/display/full versions
    
    Returns:
        Dict with data URLs for each derivative:
        {
            "orig": "data:...",      # Original (orientation corrected only)
            "clean": "data:...",     # Cropped version
            "full": "data:...",      # High-res clean
            "display": "data:...",   # Medium-res for main view
            "thumb": "data:..."      # Thumbnail
        }
    """
    try:
        # Load image
        img = Image.open(BytesIO(content))
        
        # Step 1: Correct EXIF orientation
        img = correct_exif_orientation(img)
        
        # Step 2: Convert to RGB
        img = convert_to_rgb(img)
        
        # Store original (orientation corrected)
        orig_url = image_to_data_url(smart_resize(img, FULL_MAX_WIDTH, FULL_MAX_HEIGHT), IMAGE_QUALITY_FULL)
        
        # Step 3: Crop branding
        cleaned = crop_branding(img, crop_bottom=crop_bottom, crop_top=crop_top)
        
        result = {
            "orig": orig_url,
            "clean": image_to_data_url(smart_resize(cleaned, FULL_MAX_WIDTH, FULL_MAX_HEIGHT), IMAGE_QUALITY_FULL),
        }
        
        if generate_derivatives:
            # Full resolution (clean)
            result["full"] = image_to_data_url(
                smart_resize(cleaned, FULL_MAX_WIDTH, FULL_MAX_HEIGHT), 
                IMAGE_QUALITY_FULL
            )
            
            # Display resolution
            result["display"] = image_to_data_url(
                smart_resize(cleaned, DISPLAY_MAX_WIDTH, DISPLAY_MAX_HEIGHT), 
                IMAGE_QUALITY_DISPLAY
            )
            
            # Thumbnail
            result["thumb"] = image_to_data_url(
                create_thumbnail(cleaned, THUMB_WIDTH, THUMB_HEIGHT),
                IMAGE_QUALITY_THUMB
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Image processing error: {e}")
        raise ImageCleaningError(f"Failed to process image: {e}")


async def clean_vehicle_images(
    vehicle_doc: dict,
    db,
    crop_bottom: int = CROP_BOTTOM_PIXELS,
    crop_top: int = CROP_TOP_PIXELS,
    force_reprocess: bool = False
) -> Dict:
    """
    Process all images for a vehicle document.
    
    Args:
        vehicle_doc: MongoDB vehicle document
        db: Database connection
        crop_bottom: Pixels to crop from bottom
        crop_top: Pixels to crop from top
        force_reprocess: If True, reprocess even if clean images exist
    
    Returns:
        Processing result dict
    """
    vehicle_id = str(vehicle_doc.get("_id"))
    images = vehicle_doc.get("images", [])
    
    if not images:
        return {"vehicle_id": vehicle_id, "status": "no_images", "processed": 0}
    
    processed = 0
    skipped = 0
    errors = []
    updated_images = []
    
    for img in images:
        try:
            # Check if already processed
            if not force_reprocess and img.get("clean"):
                updated_images.append(img)
                skipped += 1
                continue
            
            # Get source URL
            source_url = img.get("url") or img.get("orig")
            if not source_url:
                updated_images.append(img)
                skipped += 1
                continue
            
            # Skip if already a data URL (already processed)
            if source_url.startswith("data:") and not force_reprocess:
                updated_images.append(img)
                skipped += 1
                continue
            
            # Download and process
            logger.info(f"Processing image for vehicle {vehicle_id}: {source_url[:50]}...")
            content = await download_image(source_url)
            derivatives = process_image_for_clean_storage(content, crop_bottom, crop_top)
            
            # Update image object
            updated_img = {
                **img,
                "orig": derivatives.get("orig", source_url),
                "clean": derivatives["clean"],
                "full": derivatives["full"],
                "display": derivatives["display"],
                "thumb": derivatives["thumb"],
                "url": derivatives["display"],  # Update URL to use clean display
                "thumbnail_url": derivatives["thumb"],
            }
            updated_images.append(updated_img)
            processed += 1
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            errors.append(str(e)[:100])
            updated_images.append(img)  # Keep original
    
    # Update vehicle document in database
    if processed > 0:
        await db["admin_vehicles"].update_one(
            {"_id": vehicle_doc["_id"]},
            {"$set": {"images": updated_images}}
        )
    
    return {
        "vehicle_id": vehicle_id,
        "status": "processed",
        "processed": processed,
        "skipped": skipped,
        "errors": errors,
    }


async def run_batch_image_cleaning(
    db,
    crop_bottom: int = CROP_BOTTOM_PIXELS,
    crop_top: int = CROP_TOP_PIXELS,
    force_reprocess: bool = False,
    limit: int = 100
) -> Dict:
    """
    Run batch image cleaning on all vehicles.
    
    Args:
        db: Database connection
        crop_bottom: Pixels to crop from bottom
        crop_top: Pixels to crop from top
        force_reprocess: Reprocess all images
        limit: Max vehicles to process
    
    Returns:
        Batch processing result
    """
    collection = db["admin_vehicles"]
    
    # Find vehicles with images that need processing
    query = {}
    if not force_reprocess:
        # Only process vehicles where at least one image doesn't have 'clean' field
        query = {
            "images": {"$exists": True, "$ne": []},
            "$or": [
                {"images.clean": {"$exists": False}},
                {"images": {"$elemMatch": {"clean": {"$exists": False}}}}
            ]
        }
    
    cursor = collection.find(query).limit(limit)
    vehicles = await cursor.to_list(length=limit)
    
    total_processed = 0
    total_skipped = 0
    total_errors = []
    vehicle_results = []
    
    for vehicle in vehicles:
        result = await clean_vehicle_images(
            vehicle, db, crop_bottom, crop_top, force_reprocess
        )
        total_processed += result["processed"]
        total_skipped += result["skipped"]
        total_errors.extend(result.get("errors", []))
        vehicle_results.append({
            "vehicle_id": result["vehicle_id"],
            "processed": result["processed"],
            "status": result["status"]
        })
    
    return {
        "vehicles_checked": len(vehicles),
        "images_processed": total_processed,
        "images_skipped": total_skipped,
        "errors": total_errors[:10],
        "vehicle_results": vehicle_results[:20],
    }
