"""
Vehicle Image Storage Service

This module handles image uploads with persistence to MongoDB.
Images are stored as Base64-encoded data URLs directly in the database,
ensuring they persist across deploys/restarts.

Features:
- EXIF orientation auto-correction (fixes sideways photos from phones)
- High-quality resizing with proper aspect ratio preservation
- WebP conversion for optimal file size without quality loss

For high-volume scenarios, this can be swapped to S3/R2 storage.
"""
import base64
import uuid
import logging
from typing import List, Optional, Tuple
from io import BytesIO
from PIL import Image, ExifTags
import os

logger = logging.getLogger(__name__)

# Maximum image dimensions (resize larger images while preserving aspect ratio)
MAX_WIDTH = int(os.environ.get("IMAGE_MAX_WIDTH", "1920"))
MAX_HEIGHT = int(os.environ.get("IMAGE_MAX_HEIGHT", "1440"))
THUMBNAIL_SIZE = (600, 450)
MAX_FILE_SIZE_MB = int(os.environ.get("MAX_UPLOAD_MB", "15"))
IMAGE_QUALITY = int(os.environ.get("IMAGE_QUALITY", "92"))
THUMBNAIL_QUALITY = int(os.environ.get("THUMBNAIL_QUALITY", "85"))
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}


class ImageValidationError(Exception):
    """Raised when image validation fails"""
    pass


def correct_image_orientation(img: Image.Image) -> Image.Image:
    """
    Auto-correct image orientation based on EXIF data.
    
    Many phone cameras store rotation as EXIF metadata instead of 
    physically rotating the image. This function reads that data
    and applies the correct rotation so images display properly.
    
    Args:
        img: PIL Image object
        
    Returns:
        Correctly oriented PIL Image
    """
    try:
        # Get EXIF data
        exif = img._getexif()
        if exif is None:
            return img
        
        # Find the orientation tag
        orientation_key = None
        for key, value in ExifTags.TAGS.items():
            if value == 'Orientation':
                orientation_key = key
                break
        
        if orientation_key is None or orientation_key not in exif:
            return img
        
        orientation = exif[orientation_key]
        
        # Apply rotation/flip based on EXIF orientation value
        # See: https://exiftool.org/TagNames/EXIF.html
        if orientation == 2:
            # Mirrored horizontal
            img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            # Rotated 180 degrees
            img = img.rotate(180, expand=True)
        elif orientation == 4:
            # Mirrored vertical
            img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            # Mirrored horizontal then rotated 90 CCW
            img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            img = img.rotate(90, expand=True)
        elif orientation == 6:
            # Rotated 90 CW (most common for portrait phone photos)
            img = img.rotate(-90, expand=True)
        elif orientation == 7:
            # Mirrored horizontal then rotated 90 CW
            img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            img = img.rotate(-90, expand=True)
        elif orientation == 8:
            # Rotated 90 CCW
            img = img.rotate(90, expand=True)
        
        logger.info(f"Corrected image orientation (EXIF orientation: {orientation})")
        return img
        
    except (AttributeError, KeyError, TypeError) as e:
        # No EXIF data or orientation tag - return image as-is
        logger.debug(f"No EXIF orientation data found: {e}")
        return img


def smart_resize(img: Image.Image, max_width: int, max_height: int) -> Image.Image:
    """
    Resize image while preserving aspect ratio and maintaining quality.
    
    Uses high-quality LANCZOS resampling and only resizes if necessary.
    
    Args:
        img: PIL Image object
        max_width: Maximum width
        max_height: Maximum height
        
    Returns:
        Resized PIL Image (or original if already within bounds)
    """
    original_width, original_height = img.size
    
    # Check if resize is needed
    if original_width <= max_width and original_height <= max_height:
        return img
    
    # Calculate aspect ratio preserving dimensions
    ratio = min(max_width / original_width, max_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    
    # Use high-quality LANCZOS resampling
    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    logger.info(f"Resized image from {original_width}x{original_height} to {new_width}x{new_height}")
    return resized


def convert_to_rgb(img: Image.Image) -> Image.Image:
    """
    Convert image to RGB mode, handling transparency properly.
    
    Args:
        img: PIL Image object
        
    Returns:
        RGB PIL Image
    """
    if img.mode == 'RGB':
        return img
    
    if img.mode in ('RGBA', 'P', 'LA'):
        # Create white background for transparent images
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'RGBA':
            background.paste(img, mask=img.split()[3])
        elif img.mode == 'LA':
            background.paste(img, mask=img.split()[1])
        else:
            # Mode P (palette) - convert first
            img_rgba = img.convert('RGBA')
            background.paste(img_rgba, mask=img_rgba.split()[3])
        return background
    
    # Other modes (L, CMYK, etc.)
    return img.convert('RGB')


def validate_image_file(filename: str, content: bytes, content_type: Optional[str] = None) -> None:
    """
    Validate an uploaded image file.
    
    Raises:
        ImageValidationError: If validation fails
    """
    # Check file extension
    ext = os.path.splitext(filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        raise ImageValidationError(
            f"Invalid file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise ImageValidationError(
            f"File too large ({size_mb:.1f}MB). Maximum: {MAX_FILE_SIZE_MB}MB"
        )
    
    # Check content type if provided
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise ImageValidationError(
            f"Invalid content type '{content_type}'. Allowed: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    # Try to open as image to verify it's valid
    try:
        img = Image.open(BytesIO(content))
        img.verify()
    except Exception as e:
        raise ImageValidationError(f"Invalid or corrupted image file: {str(e)}")


def process_image(content: bytes, optimize: bool = True) -> Tuple[bytes, str]:
    """
    Process an image with EXIF correction, proper resizing, and WebP conversion.
    
    This function:
    1. Auto-corrects orientation from EXIF data (fixes sideways phone photos)
    2. Converts to RGB mode (handles transparency)
    3. Resizes with aspect ratio preservation using high-quality resampling
    4. Converts to WebP format with high quality settings
    
    Args:
        content: Raw image bytes
        optimize: Whether to resize the image (always processes orientation)
        
    Returns:
        Tuple of (processed_bytes, mime_type)
    """
    img = Image.open(BytesIO(content))
    
    # Step 1: Auto-correct EXIF orientation (critical for phone photos)
    img = correct_image_orientation(img)
    
    # Step 2: Convert to RGB
    img = convert_to_rgb(img)
    
    # Step 3: Smart resize if needed (preserves aspect ratio)
    if optimize:
        img = smart_resize(img, MAX_WIDTH, MAX_HEIGHT)
    
    # Step 4: Save as high-quality WebP
    output = BytesIO()
    img.save(
        output, 
        format='WEBP', 
        quality=IMAGE_QUALITY, 
        method=6,  # Highest quality compression method
        optimize=True
    )
    output.seek(0)
    
    return output.read(), 'image/webp'


def create_thumbnail(content: bytes) -> bytes:
    """
    Create a high-quality thumbnail version of the image.
    
    Applies EXIF correction before thumbnailing to ensure
    correct orientation in gallery views.
    """
    img = Image.open(BytesIO(content))
    
    # Apply EXIF orientation correction
    img = correct_image_orientation(img)
    
    # Convert to RGB
    img = convert_to_rgb(img)
    
    # Create thumbnail with aspect ratio preservation
    # Use LANCZOS for high-quality downsampling
    img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
    
    output = BytesIO()
    img.save(
        output, 
        format='WEBP', 
        quality=THUMBNAIL_QUALITY, 
        method=6,
        optimize=True
    )
    output.seek(0)
    
    return output.read()


def encode_image_to_data_url(content: bytes, mime_type: str = 'image/webp') -> str:
    """Convert image bytes to a data URL."""
    b64 = base64.b64encode(content).decode('utf-8')
    return f"data:{mime_type};base64,{b64}"


def decode_data_url(data_url: str) -> Tuple[bytes, str]:
    """
    Decode a data URL back to bytes.
    
    Returns:
        Tuple of (bytes, mime_type)
    """
    if not data_url.startswith('data:'):
        raise ValueError("Invalid data URL")
    
    header, b64_data = data_url.split(',', 1)
    mime_type = header.split(';')[0].replace('data:', '')
    content = base64.b64decode(b64_data)
    
    return content, mime_type


class VehicleImage:
    """Represents a vehicle image with metadata."""
    
    def __init__(
        self,
        url: str,
        is_primary: bool = False,
        thumbnail_url: Optional[str] = None,
        original_filename: Optional[str] = None,
        upload_id: Optional[str] = None,
    ):
        self.url = url
        self.is_primary = is_primary
        self.thumbnail_url = thumbnail_url
        self.original_filename = original_filename
        self.upload_id = upload_id or str(uuid.uuid4())
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB storage."""
        return {
            "url": self.url,
            "is_primary": self.is_primary,
            "thumbnail_url": self.thumbnail_url,
            "original_filename": self.original_filename,
            "upload_id": self.upload_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VehicleImage':
        """Create from dictionary."""
        return cls(
            url=data.get("url", ""),
            is_primary=data.get("is_primary", False),
            thumbnail_url=data.get("thumbnail_url"),
            original_filename=data.get("original_filename"),
            upload_id=data.get("upload_id"),
        )


async def process_and_store_image(
    content: bytes,
    filename: str,
    content_type: Optional[str] = None,
    is_primary: bool = False,
    create_thumb: bool = True,
) -> VehicleImage:
    """
    Process an uploaded image and prepare for storage.
    
    Args:
        content: Raw file bytes
        filename: Original filename
        content_type: MIME type
        is_primary: Whether this is the primary image
        create_thumb: Whether to create a thumbnail
        
    Returns:
        VehicleImage object ready for storage
    """
    # Validate
    validate_image_file(filename, content, content_type)
    
    # Process (resize, convert to WebP)
    processed_content, mime_type = process_image(content)
    
    # Create data URL
    url = encode_image_to_data_url(processed_content, mime_type)
    
    # Create thumbnail if requested
    thumbnail_url = None
    if create_thumb:
        thumb_content = create_thumbnail(content)
        thumbnail_url = encode_image_to_data_url(thumb_content, mime_type)
    
    return VehicleImage(
        url=url,
        is_primary=is_primary,
        thumbnail_url=thumbnail_url,
        original_filename=filename,
    )


def migrate_legacy_photo_urls(photo_urls: List[str]) -> List[dict]:
    """
    Migrate legacy string URLs to new images[] schema.
    
    Legacy format: ["/admin-vehicles/123/abc.jpg", ...]
    New format: [{"url": "...", "is_primary": true/false}, ...]
    """
    if not photo_urls:
        return []
    
    images = []
    for i, url in enumerate(photo_urls):
        # Skip if already in new format (dict)
        if isinstance(url, dict):
            images.append(url)
            continue
        
        # Convert string URL to new format
        images.append({
            "url": url,
            "is_primary": i == 0,
            "thumbnail_url": None,
            "original_filename": None,
            "upload_id": str(uuid.uuid4()),
        })
    
    return images


def normalize_images_field(doc: dict) -> List[dict]:
    """
    Normalize various image field formats to consistent images[] schema.
    
    Handles:
    - photo_urls (legacy string array)
    - images (new format)
    - imageUrls (alternative naming)
    """
    # Check for images field first (new format)
    if "images" in doc and doc["images"]:
        images = doc["images"]
        # Ensure each item is a dict
        return [
            img if isinstance(img, dict) else {"url": img, "is_primary": False}
            for img in images
        ]
    
    # Check for photo_urls (legacy format)
    if "photo_urls" in doc and doc["photo_urls"]:
        return migrate_legacy_photo_urls(doc["photo_urls"])
    
    # Check for imageUrls (alternative naming)
    if "imageUrls" in doc and doc["imageUrls"]:
        return migrate_legacy_photo_urls(doc["imageUrls"])
    
    return []
