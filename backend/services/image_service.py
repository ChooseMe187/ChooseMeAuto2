"""
Vehicle Image Storage Service

This module handles image uploads with persistence to MongoDB.
Images are stored as Base64-encoded data URLs directly in the database,
ensuring they persist across deploys/restarts.

For high-volume scenarios, this can be swapped to S3/R2 storage.
"""
import base64
import uuid
import logging
from typing import List, Optional, Tuple
from io import BytesIO
from PIL import Image
import os

logger = logging.getLogger(__name__)

# Maximum image dimensions (resize larger images)
MAX_WIDTH = 1200
MAX_HEIGHT = 900
THUMBNAIL_SIZE = (400, 300)
MAX_FILE_SIZE_MB = 8
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}


class ImageValidationError(Exception):
    """Raised when image validation fails"""
    pass


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
    Process an image: resize if needed, convert to WebP for optimization.
    
    Args:
        content: Raw image bytes
        optimize: Whether to optimize/resize the image
        
    Returns:
        Tuple of (processed_bytes, mime_type)
    """
    img = Image.open(BytesIO(content))
    
    # Convert to RGB if necessary (for PNG with transparency)
    if img.mode in ('RGBA', 'P'):
        # Create white background
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'RGBA':
            background.paste(img, mask=img.split()[3])
        else:
            background.paste(img)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize if too large
    if optimize and (img.width > MAX_WIDTH or img.height > MAX_HEIGHT):
        img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)
        logger.info(f"Resized image to {img.width}x{img.height}")
    
    # Save as WebP for better compression
    output = BytesIO()
    img.save(output, format='WEBP', quality=85, optimize=True)
    output.seek(0)
    
    return output.read(), 'image/webp'


def create_thumbnail(content: bytes) -> bytes:
    """Create a thumbnail version of the image."""
    img = Image.open(BytesIO(content))
    
    # Convert to RGB
    if img.mode in ('RGBA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'RGBA':
            background.paste(img, mask=img.split()[3])
        else:
            background.paste(img)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
    
    output = BytesIO()
    img.save(output, format='WEBP', quality=75, optimize=True)
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
