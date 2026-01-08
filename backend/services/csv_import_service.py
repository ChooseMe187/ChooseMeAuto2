"""
CSV Import Service for Vehicle Inventory

Handles parsing, validation, and upsert logic for CSV vehicle imports.
Primary key: VIN (17-character unique identifier)
"""
import csv
import io
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# CSV Configuration
MAX_CSV_SIZE_MB = 5
MAX_CSV_SIZE_BYTES = MAX_CSV_SIZE_MB * 1024 * 1024
MAX_PREVIEW_ROWS = 20

# Required fields for vehicle creation
REQUIRED_FIELDS = ['vin', 'year', 'make', 'model', 'price']

# All supported CSV columns
SUPPORTED_COLUMNS = [
    'vin', 'year', 'make', 'model', 'price', 'trim', 'mileage', 'stock_number',
    'condition', 'exterior_color', 'interior_color', 'transmission', 'drivetrain',
    'fuel_type', 'body_style', 'engine', 'carfax_url', 'window_sticker_url',
    'primary_image_url', 'image_urls', 'is_featured_homepage', 'featured_rank',
    'call_for_availability_enabled', 'is_active'
]

# VIN validation regex (17 alphanumeric, no I, O, Q)
VIN_REGEX = re.compile(r'^[A-HJ-NPR-Z0-9]{17}$', re.IGNORECASE)


class CSVValidationError(Exception):
    """Raised when CSV validation fails"""
    pass


def validate_vin(vin: str) -> Tuple[bool, str]:
    """Validate VIN format (17 characters, alphanumeric, no I/O/Q)"""
    if not vin:
        return False, "VIN is required"
    vin = vin.strip().upper()
    if len(vin) != 17:
        return False, f"VIN must be 17 characters (got {len(vin)})"
    if not VIN_REGEX.match(vin):
        return False, "VIN contains invalid characters"
    return True, vin


def normalize_boolean(value: Any) -> Optional[bool]:
    """Normalize various boolean representations"""
    if value is None or value == '':
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value = value.strip().lower()
        if value in ('true', '1', 'yes', 'y'):
            return True
        if value in ('false', '0', 'no', 'n'):
            return False
    return None


def normalize_number(value: Any, field_type: str = 'int') -> Optional[Any]:
    """Normalize numeric values, handling currency symbols and commas"""
    if value is None or value == '':
        return None
    if isinstance(value, (int, float)):
        return int(value) if field_type == 'int' else float(value)
    if isinstance(value, str):
        # Remove currency symbols, commas, spaces
        cleaned = re.sub(r'[$,\s]', '', value.strip())
        try:
            if field_type == 'int':
                return int(float(cleaned))
            return float(cleaned)
        except ValueError:
            return None
    return None


def parse_image_urls(value: str) -> List[str]:
    """Parse image URLs from pipe-separated or JSON array format"""
    if not value or not value.strip():
        return []
    
    value = value.strip()
    
    # Try JSON array first
    if value.startswith('['):
        try:
            import json
            urls = json.loads(value)
            if isinstance(urls, list):
                return [u.strip() for u in urls if u and u.strip()]
        except json.JSONDecodeError:
            pass
    
    # Pipe-separated
    if '|' in value:
        return [u.strip() for u in value.split('|') if u and u.strip()]
    
    # Single URL
    return [value] if value else []


def validate_row(row: Dict[str, Any], row_num: int) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Validate and normalize a single CSV row.
    
    Returns:
        (is_valid, normalized_data, errors)
    """
    errors = []
    normalized = {}
    
    # Validate VIN (required, unique identifier)
    vin_valid, vin_result = validate_vin(row.get('vin', ''))
    if not vin_valid:
        errors.append(f"Row {row_num}: {vin_result}")
    else:
        normalized['vin'] = vin_result
    
    # Validate other required fields
    for field in REQUIRED_FIELDS:
        if field == 'vin':
            continue
        value = row.get(field, '').strip() if row.get(field) else ''
        if not value:
            errors.append(f"Row {row_num}: Missing required field '{field}'")
    
    # Normalize year
    year = normalize_number(row.get('year'), 'int')
    if year:
        if year < 1900 or year > datetime.now().year + 2:
            errors.append(f"Row {row_num}: Invalid year '{row.get('year')}'")
        else:
            normalized['year'] = year
    
    # Normalize price
    price = normalize_number(row.get('price'), 'int')
    if price is not None:
        if price < 0:
            errors.append(f"Row {row_num}: Price cannot be negative")
        else:
            normalized['price'] = price
    
    # Normalize mileage
    mileage = normalize_number(row.get('mileage'), 'int')
    if mileage is not None:
        if mileage < 0:
            errors.append(f"Row {row_num}: Mileage cannot be negative")
        else:
            normalized['mileage'] = mileage
    
    # Normalize text fields
    text_fields = ['make', 'model', 'trim', 'stock_number', 'condition', 
                   'exterior_color', 'interior_color', 'transmission', 
                   'drivetrain', 'fuel_type', 'body_style', 'engine',
                   'carfax_url', 'window_sticker_url', 'primary_image_url']
    
    for field in text_fields:
        value = row.get(field, '')
        if value and isinstance(value, str):
            normalized[field] = value.strip()
    
    # Normalize condition
    if 'condition' in normalized:
        condition = normalized['condition'].lower()
        if condition in ('new', 'nuevo'):
            normalized['condition'] = 'New'
        elif condition in ('used', 'usado', 'pre-owned'):
            normalized['condition'] = 'Used'
        else:
            normalized['condition'] = 'Used'  # Default
    
    # Normalize booleans
    bool_fields = ['is_featured_homepage', 'call_for_availability_enabled', 'is_active']
    for field in bool_fields:
        value = normalize_boolean(row.get(field))
        if value is not None:
            normalized[field] = value
    
    # Normalize featured_rank
    featured_rank = normalize_number(row.get('featured_rank'), 'int')
    if featured_rank is not None:
        normalized['featured_rank'] = featured_rank
    
    # Parse image URLs
    primary_image = row.get('primary_image_url', '').strip()
    additional_images = parse_image_urls(row.get('image_urls', ''))
    
    if primary_image or additional_images:
        images = []
        if primary_image:
            images.append({'url': primary_image, 'is_primary': True})
        for img_url in additional_images:
            if img_url != primary_image:
                images.append({'url': img_url, 'is_primary': False})
        if images:
            normalized['images'] = images
    
    return len(errors) == 0, normalized, errors


def parse_csv_content(content: bytes) -> Tuple[List[Dict], List[str], List[str]]:
    """
    Parse CSV content and return rows, headers, and any parsing errors.
    
    Returns:
        (rows, headers, errors)
    """
    errors = []
    
    # Try different encodings
    for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
        try:
            text = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise CSVValidationError("Unable to decode CSV file. Please use UTF-8 encoding.")
    
    # Parse CSV
    reader = csv.DictReader(io.StringIO(text))
    
    # Get headers
    headers = reader.fieldnames or []
    if not headers:
        raise CSVValidationError("CSV file has no headers")
    
    # Normalize headers (lowercase, strip whitespace)
    header_map = {h.lower().strip().replace(' ', '_'): h for h in headers}
    
    # Check for required columns
    missing_required = []
    for field in REQUIRED_FIELDS:
        if field not in header_map:
            missing_required.append(field)
    
    if missing_required:
        raise CSVValidationError(f"Missing required columns: {', '.join(missing_required)}")
    
    # Parse rows
    rows = []
    for i, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
        # Normalize keys
        normalized_row = {}
        for key, value in row.items():
            normalized_key = key.lower().strip().replace(' ', '_')
            normalized_row[normalized_key] = value
        rows.append(normalized_row)
    
    return rows, list(header_map.keys()), errors


async def process_csv_import(
    content: bytes,
    db,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Process CSV import with validation and upsert logic.
    
    Args:
        content: Raw CSV file content
        db: MongoDB database connection
        dry_run: If True, only validate and preview (no database changes)
    
    Returns:
        Import result with counts and row-level details
    """
    result = {
        'success': True,
        'dry_run': dry_run,
        'counts': {
            'total_rows': 0,
            'valid_rows': 0,
            'to_create': 0,
            'to_update': 0,
            'skipped': 0,
            'created': 0,
            'updated': 0,
        },
        'preview': [],
        'errors': [],
        'skipped_rows': [],
    }
    
    # Check file size
    if len(content) > MAX_CSV_SIZE_BYTES:
        raise CSVValidationError(f"CSV file too large. Maximum size is {MAX_CSV_SIZE_MB}MB")
    
    # Parse CSV
    rows, headers, parse_errors = parse_csv_content(content)
    result['errors'].extend(parse_errors)
    result['counts']['total_rows'] = len(rows)
    result['headers'] = headers
    
    if not rows:
        raise CSVValidationError("CSV file contains no data rows")
    
    # Get existing VINs from database
    collection = db["admin_vehicles"]
    existing_vins = {}
    async for doc in collection.find({}, {'vin': 1, '_id': 1}):
        if doc.get('vin'):
            existing_vins[doc['vin'].upper()] = str(doc['_id'])
    
    # Validate and categorize rows
    valid_rows = []
    
    for i, row in enumerate(rows, start=2):
        is_valid, normalized, row_errors = validate_row(row, i)
        
        if not is_valid:
            result['errors'].extend(row_errors)
            result['skipped_rows'].append({
                'row': i,
                'vin': row.get('vin', 'N/A'),
                'reasons': row_errors,
            })
            result['counts']['skipped'] += 1
            continue
        
        # Check if VIN exists (for upsert logic)
        vin = normalized.get('vin', '').upper()
        existing_id = existing_vins.get(vin)
        
        row_info = {
            'row': i,
            'vin': vin,
            'vehicle': f"{normalized.get('year', '')} {normalized.get('make', '')} {normalized.get('model', '')}",
            'action': 'update' if existing_id else 'create',
            'data': normalized,
            'existing_id': existing_id,
        }
        
        if existing_id:
            result['counts']['to_update'] += 1
        else:
            result['counts']['to_create'] += 1
        
        result['counts']['valid_rows'] += 1
        valid_rows.append(row_info)
        
        # Add to preview (first N rows)
        if len(result['preview']) < MAX_PREVIEW_ROWS:
            result['preview'].append({
                'row': row_info['row'],
                'vin': row_info['vin'],
                'vehicle': row_info['vehicle'],
                'action': row_info['action'],
                'price': normalized.get('price'),
            })
    
    # If dry run, return preview only
    if dry_run:
        return result
    
    # Perform actual import
    now = datetime.now(timezone.utc)
    
    for row_info in valid_rows:
        data = row_info['data']
        vin = row_info['vin']
        
        try:
            if row_info['action'] == 'update':
                # Update existing vehicle (partial update)
                update_data = {k: v for k, v in data.items() if v is not None}
                update_data['updated_at'] = now
                
                await collection.update_one(
                    {'vin': vin},
                    {'$set': update_data}
                )
                result['counts']['updated'] += 1
                logger.info(f"CSV Import: Updated vehicle VIN={vin}")
                
            else:
                # Create new vehicle
                data['created_at'] = now
                data['updated_at'] = now
                data['is_active'] = data.get('is_active', True)
                
                # Generate stock number if not provided
                if not data.get('stock_number'):
                    data['stock_number'] = f"CMA{uuid.uuid4().hex[:6].upper()}"
                
                await collection.insert_one(data)
                result['counts']['created'] += 1
                logger.info(f"CSV Import: Created vehicle VIN={vin}")
                
        except Exception as e:
            logger.error(f"CSV Import error for VIN={vin}: {e}")
            result['errors'].append(f"Database error for VIN {vin}: {str(e)}")
            result['counts']['skipped'] += 1
    
    result['success'] = len(result['errors']) == 0 or result['counts']['created'] + result['counts']['updated'] > 0
    
    return result


def generate_csv_template() -> str:
    """Generate a CSV template with headers and sample row"""
    headers = [
        'vin', 'year', 'make', 'model', 'price', 'trim', 'mileage', 'stock_number',
        'condition', 'exterior_color', 'interior_color', 'transmission', 'drivetrain',
        'body_style', 'carfax_url', 'primary_image_url', 'image_urls',
        'is_featured_homepage', 'featured_rank'
    ]
    
    sample_row = [
        '1HGCM82633A123456',  # vin
        '2024',              # year
        'Honda',             # make
        'Accord',            # model
        '32500',             # price
        'Sport',             # trim
        '15000',             # mileage
        'CMA001',            # stock_number
        'Used',              # condition
        'Black',             # exterior_color
        'Black',             # interior_color
        'Automatic',         # transmission
        'FWD',               # drivetrain
        'Sedan',             # body_style
        '',                  # carfax_url
        '',                  # primary_image_url
        '',                  # image_urls
        'false',             # is_featured_homepage
        '',                  # featured_rank
    ]
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerow(sample_row)
    
    return output.getvalue()


# Need to import uuid for stock number generation
import uuid
