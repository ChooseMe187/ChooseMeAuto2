#!/usr/bin/env python3
"""
Backend API Testing for Choose Me Auto Car Dealership
Tests the Vehicle Image Pipeline as specified in the review request.
"""

import requests
import json
import os
import base64
import io
from datetime import datetime
from PIL import Image

# Get backend URL from frontend .env
BACKEND_URL = "https://autodealership.preview.emergentagent.com/api"
ADMIN_TOKEN = "cma-admin-2c8e1cd0f9b70c27827d310304fd7b4c"

# Test data
NEW_VEHICLE_STOCK = "CMAEE34F7"  # 2025 Honda Accord
USED_VEHICLE_STOCK = "CMA5A1BBF"  # 2023 Toyota Camry

def create_test_image(width=800, height=600, format='JPEG', color=(255, 0, 0)):
    """Create a test image in memory"""
    img = Image.new('RGB', (width, height), color)
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)
    return buffer.getvalue()

def create_invalid_file():
    """Create an invalid file (text file with image extension)"""
    return b"This is not an image file"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"TESTING: {test_name}")
    print(f"{'='*60}")

def print_result(test_name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   Details: {details}")

# IMG-1: Upload Flow Test
def test_img1_upload_flow():
    """IMG-1: Test vehicle image upload flow"""
    print_test_header("IMG-1: Vehicle Image Upload Flow")
    
    # First, create a test vehicle
    headers = {
        'Content-Type': 'application/json',
        'x-admin-token': ADMIN_TOKEN
    }
    
    test_vehicle = {
        "vin": "IMG1TEST123456789",
        "year": 2024,
        "make": "Test",
        "model": "ImageUpload",
        "trim": "Test Trim",
        "price": 30000,
        "mileage": 0,
        "condition": "New",
        "body_style": "Sedan",
        "exterior_color": "Blue",
        "interior_color": "Black",
        "is_active": True
    }
    
    try:
        # Create vehicle
        response = requests.post(f"{BACKEND_URL}/admin/vehicles", 
                               headers=headers, 
                               json=test_vehicle, 
                               timeout=10)
        
        if response.status_code != 201:
            print_result("Create test vehicle", False, f"Status code: {response.status_code}")
            return False, None
            
        created_vehicle = response.json()
        vehicle_id = created_vehicle.get('id')
        print_result("Create test vehicle", True, f"Created vehicle with ID: {vehicle_id}")
        
        # Create test images
        test_image_jpg = create_test_image(format='JPEG', color=(255, 0, 0))  # Red
        test_image_png = create_test_image(format='PNG', color=(0, 255, 0))   # Green
        
        # Upload images
        files = [
            ('files', ('test1.jpg', test_image_jpg, 'image/jpeg')),
            ('files', ('test2.png', test_image_png, 'image/png'))
        ]
        
        upload_headers = {'x-admin-token': ADMIN_TOKEN}
        
        response = requests.post(f"{BACKEND_URL}/admin/vehicles/{vehicle_id}/photos",
                               headers=upload_headers,
                               files=files,
                               timeout=30)
        
        if response.status_code != 200:
            print_result("Upload images", False, f"Status code: {response.status_code}, Response: {response.text}")
            return False, vehicle_id
            
        upload_result = response.json()
        
        # Verify response structure
        required_fields = ['images', 'photo_urls', 'uploaded_count']
        for field in required_fields:
            if field not in upload_result:
                print_result("Upload response structure", False, f"Missing field: {field}")
                return False, vehicle_id
        
        # Verify uploaded count
        if upload_result['uploaded_count'] != 2:
            print_result("Upload count", False, f"Expected 2, got {upload_result['uploaded_count']}")
            return False, vehicle_id
            
        # Verify images are Base64 data URLs
        images = upload_result['images']
        if len(images) != 2:
            print_result("Images array length", False, f"Expected 2, got {len(images)}")
            return False, vehicle_id
            
        for i, img in enumerate(images):
            if not img.get('url', '').startswith('data:image/webp;base64,'):
                print_result(f"Image {i+1} data URL format", False, f"URL: {img.get('url', '')[:50]}...")
                return False, vehicle_id
                
        # Verify first image is primary
        if not images[0].get('is_primary'):
            print_result("First image primary flag", False, "First image should be primary")
            return False, vehicle_id
            
        print_result("IMG-1: Upload Flow", True, f"Successfully uploaded {upload_result['uploaded_count']} images")
        return True, vehicle_id
        
    except Exception as e:
        print_result("IMG-1: Upload Flow", False, f"Exception: {str(e)}")
        return False, None

# IMG-2: Image Data Contract Test
def test_img2_data_contract(vehicle_id):
    """IMG-2: Test image data contract in API responses"""
    print_test_header("IMG-2: Image Data Contract Test")
    
    headers = {'x-admin-token': ADMIN_TOKEN}
    
    try:
        # Test admin vehicles endpoint
        response = requests.get(f"{BACKEND_URL}/admin/vehicles/{vehicle_id}", 
                              headers=headers, 
                              timeout=10)
        
        if response.status_code != 200:
            print_result("Admin vehicle endpoint", False, f"Status code: {response.status_code}")
            return False
            
        admin_vehicle = response.json()
        
        # Verify admin response structure
        if 'images' not in admin_vehicle:
            print_result("Admin images field", False, "Missing images field")
            return False
            
        if 'photo_urls' not in admin_vehicle:
            print_result("Admin photo_urls field", False, "Missing photo_urls field")
            return False
            
        images = admin_vehicle['images']
        if not images:
            print_result("Admin images array", False, "Images array is empty")
            return False
            
        # Check image structure
        sample_image = images[0]
        required_image_fields = ['url', 'is_primary', 'upload_id']
        for field in required_image_fields:
            if field not in sample_image:
                print_result(f"Admin image {field} field", False, f"Missing {field} in image object")
                return False
                
        print_result("Admin endpoint data contract", True, "All required fields present")
        
        # Test public vehicles endpoint
        vehicle_stock = admin_vehicle.get('stock_number')
        if not vehicle_stock:
            print_result("Vehicle stock number", False, "No stock number found")
            return False
            
        response = requests.get(f"{BACKEND_URL}/vehicles/{vehicle_stock}", timeout=10)
        
        if response.status_code != 200:
            print_result("Public vehicle endpoint", False, f"Status code: {response.status_code}")
            return False
            
        public_vehicle = response.json()
        
        # Verify public response has same schema
        if 'images' not in public_vehicle:
            print_result("Public images field", False, "Missing images field")
            return False
            
        if 'photo_urls' not in public_vehicle:
            print_result("Public photo_urls field", False, "Missing photo_urls field")
            return False
            
        # Verify images match
        if len(public_vehicle['images']) != len(admin_vehicle['images']):
            print_result("Public/Admin images count match", False, 
                        f"Admin: {len(admin_vehicle['images'])}, Public: {len(public_vehicle['images'])}")
            return False
            
        print_result("IMG-2: Data Contract", True, "Both admin and public endpoints return correct schema")
        return True
        
    except Exception as e:
        print_result("IMG-2: Data Contract", False, f"Exception: {str(e)}")
        return False

# IMG-3: Migration Test
def test_img3_migration():
    """IMG-3: Test image migration endpoint"""
    print_test_header("IMG-3: Image Migration Test")
    
    headers = {
        'Content-Type': 'application/json',
        'x-admin-token': ADMIN_TOKEN
    }
    
    try:
        # Run migration
        response = requests.post(f"{BACKEND_URL}/admin/migrate-images", 
                               headers=headers, 
                               timeout=30)
        
        if response.status_code != 200:
            print_result("Migration endpoint", False, f"Status code: {response.status_code}")
            return False
            
        migration_result = response.json()
        
        # Verify response structure
        required_fields = ['success', 'migrated', 'skipped', 'total']
        for field in required_fields:
            if field not in migration_result:
                print_result(f"Migration {field} field", False, f"Missing {field}")
                return False
                
        if not migration_result['success']:
            print_result("Migration success", False, "Migration reported failure")
            return False
            
        # Run migration again to test idempotency
        response2 = requests.post(f"{BACKEND_URL}/admin/migrate-images", 
                                headers=headers, 
                                timeout=30)
        
        if response2.status_code != 200:
            print_result("Migration idempotency", False, f"Second run failed: {response2.status_code}")
            return False
            
        migration_result2 = response2.json()
        
        # Second run should skip more records (idempotent)
        if migration_result2['migrated'] > migration_result['migrated']:
            print_result("Migration idempotency", False, "Second run migrated more than first run")
            return False
            
        print_result("IMG-3: Migration", True, 
                    f"First run: {migration_result['migrated']} migrated, {migration_result['skipped']} skipped. "
                    f"Second run: {migration_result2['migrated']} migrated, {migration_result2['skipped']} skipped")
        return True
        
    except Exception as e:
        print_result("IMG-3: Migration", False, f"Exception: {str(e)}")
        return False

# IMG-5: Validation Test
def test_img5_validation(vehicle_id):
    """IMG-5: Test file validation"""
    print_test_header("IMG-5: File Validation Test")
    
    upload_headers = {'x-admin-token': ADMIN_TOKEN}
    
    try:
        # Test invalid file type
        invalid_file = create_invalid_file()
        files = [('files', ('test.txt', invalid_file, 'text/plain'))]
        
        response = requests.post(f"{BACKEND_URL}/admin/vehicles/{vehicle_id}/photos",
                               headers=upload_headers,
                               files=files,
                               timeout=10)
        
        if response.status_code == 200:
            # Check if it properly rejected the invalid file
            result = response.json()
            if result.get('uploaded_count', 0) > 0:
                print_result("Invalid file rejection", False, "Invalid file was accepted")
                return False
            elif 'errors' in result and len(result['errors']) > 0:
                print_result("Invalid file rejection", True, f"Properly rejected: {result['errors'][0]['error']}")
            else:
                print_result("Invalid file rejection", False, "No error reported for invalid file")
                return False
        elif response.status_code == 400:
            print_result("Invalid file rejection", True, "Invalid file properly rejected with 400")
        else:
            print_result("Invalid file rejection", False, f"Unexpected status: {response.status_code}")
            return False
        
        # Test valid file types
        valid_jpg = create_test_image(format='JPEG', color=(0, 0, 255))  # Blue
        valid_png = create_test_image(format='PNG', color=(255, 255, 0))  # Yellow
        
        files = [
            ('files', ('valid.jpg', valid_jpg, 'image/jpeg')),
            ('files', ('valid.png', valid_png, 'image/png'))
        ]
        
        response = requests.post(f"{BACKEND_URL}/admin/vehicles/{vehicle_id}/photos",
                               headers=upload_headers,
                               files=files,
                               timeout=30)
        
        if response.status_code != 200:
            print_result("Valid file upload", False, f"Status code: {response.status_code}")
            return False
            
        result = response.json()
        if result.get('uploaded_count', 0) != 2:
            print_result("Valid file upload", False, f"Expected 2 uploads, got {result.get('uploaded_count', 0)}")
            return False
            
        print_result("IMG-5: Validation", True, "Invalid files rejected, valid files accepted")
        return True
        
    except Exception as e:
        print_result("IMG-5: Validation", False, f"Exception: {str(e)}")
        return False

# IMG-6: Delete Photo Test
def test_img6_delete_photo(vehicle_id):
    """IMG-6: Test photo deletion"""
    print_test_header("IMG-6: Delete Photo Test")
    
    headers = {'x-admin-token': ADMIN_TOKEN}
    
    try:
        # Get current images
        response = requests.get(f"{BACKEND_URL}/admin/vehicles/{vehicle_id}", 
                              headers=headers, 
                              timeout=10)
        
        if response.status_code != 200:
            print_result("Get vehicle for deletion", False, f"Status code: {response.status_code}")
            return False
            
        vehicle = response.json()
        images_before = vehicle.get('images', [])
        
        if len(images_before) == 0:
            print_result("Images available for deletion", False, "No images to delete")
            return False
            
        initial_count = len(images_before)
        
        # Delete the last photo (index -1 becomes last valid index)
        delete_index = initial_count - 1
        
        response = requests.delete(f"{BACKEND_URL}/admin/vehicles/{vehicle_id}/photos/{delete_index}",
                                 headers=headers,
                                 timeout=10)
        
        if response.status_code != 200:
            print_result("Delete photo", False, f"Status code: {response.status_code}")
            return False
            
        delete_result = response.json()
        
        # Verify response structure
        if not delete_result.get('success'):
            print_result("Delete success flag", False, "Success flag is false")
            return False
            
        if 'images' not in delete_result:
            print_result("Delete response images", False, "Missing images in response")
            return False
            
        if 'photo_urls' not in delete_result:
            print_result("Delete response photo_urls", False, "Missing photo_urls in response")
            return False
            
        # Verify count decreased
        images_after = delete_result['images']
        if len(images_after) != initial_count - 1:
            print_result("Image count after deletion", False, 
                        f"Expected {initial_count - 1}, got {len(images_after)}")
            return False
            
        # Verify photo_urls matches images
        photo_urls = delete_result['photo_urls']
        if len(photo_urls) != len(images_after):
            print_result("Photo URLs count match", False, 
                        f"Images: {len(images_after)}, URLs: {len(photo_urls)}")
            return False
            
        print_result("IMG-6: Delete Photo", True, f"Successfully deleted photo, {len(images_after)} remaining")
        return True
        
    except Exception as e:
        print_result("IMG-6: Delete Photo", False, f"Exception: {str(e)}")
        return False

# IMG-7: Set Primary Photo Test
def test_img7_set_primary(vehicle_id):
    """IMG-7: Test setting primary photo"""
    print_test_header("IMG-7: Set Primary Photo Test")
    
    headers = {'x-admin-token': ADMIN_TOKEN}
    
    try:
        # Get current images
        response = requests.get(f"{BACKEND_URL}/admin/vehicles/{vehicle_id}", 
                              headers=headers, 
                              timeout=10)
        
        if response.status_code != 200:
            print_result("Get vehicle for primary test", False, f"Status code: {response.status_code}")
            return False
            
        vehicle = response.json()
        images_before = vehicle.get('images', [])
        
        if len(images_before) < 2:
            print_result("Multiple images for primary test", False, f"Need at least 2 images, have {len(images_before)}")
            return False
            
        # Find current primary
        current_primary_index = None
        for i, img in enumerate(images_before):
            if img.get('is_primary'):
                current_primary_index = i
                break
                
        # Set a different image as primary (use index 1 if current primary is 0, else use 0)
        new_primary_index = 1 if current_primary_index == 0 else 0
        
        response = requests.patch(f"{BACKEND_URL}/admin/vehicles/{vehicle_id}/photos/{new_primary_index}/primary",
                                headers=headers,
                                timeout=10)
        
        if response.status_code != 200:
            print_result("Set primary photo", False, f"Status code: {response.status_code}")
            return False
            
        primary_result = response.json()
        
        # Verify response structure
        if not primary_result.get('success'):
            print_result("Primary success flag", False, "Success flag is false")
            return False
            
        if 'images' not in primary_result:
            print_result("Primary response images", False, "Missing images in response")
            return False
            
        images_after = primary_result['images']
        
        # Verify new primary is first in array
        if not images_after[0].get('is_primary'):
            print_result("New primary is first", False, "First image is not marked as primary")
            return False
            
        # Verify only one image is marked as primary
        primary_count = sum(1 for img in images_after if img.get('is_primary'))
        if primary_count != 1:
            print_result("Single primary image", False, f"Expected 1 primary, found {primary_count}")
            return False
            
        # Verify order changed (primary should be first)
        original_primary_url = images_before[new_primary_index]['url']
        new_first_url = images_after[0]['url']
        
        if original_primary_url != new_first_url:
            print_result("Primary reordering", False, "Primary image was not moved to first position")
            return False
            
        print_result("IMG-7: Set Primary", True, "Primary photo updated and reordered correctly")
        return True
        
    except Exception as e:
        print_result("IMG-7: Set Primary", False, f"Exception: {str(e)}")
        return False

def test_vehicles_api():
    """Test 1: GET /api/vehicles - should return all vehicles with new fields"""
    print_test_header("GET /api/vehicles - All vehicles")
    
    try:
        response = requests.get(f"{BACKEND_URL}/vehicles", timeout=10)
        
        if response.status_code != 200:
            print_result("GET /api/vehicles", False, f"Status code: {response.status_code}")
            return False
            
        vehicles = response.json()
        
        if not isinstance(vehicles, list):
            print_result("GET /api/vehicles", False, "Response is not a list")
            return False
            
        if len(vehicles) == 0:
            print_result("GET /api/vehicles", False, "No vehicles returned")
            return False
            
        # Check if vehicles have new fields
        sample_vehicle = vehicles[0]
        required_fields = ['stock_id', 'carfax_url', 'window_sticker_url', 'call_for_availability_enabled', 'condition']
        
        missing_fields = []
        for field in required_fields:
            if field not in sample_vehicle:
                missing_fields.append(field)
                
        if missing_fields:
            print_result("GET /api/vehicles", False, f"Missing fields: {missing_fields}")
            return False
            
        print_result("GET /api/vehicles", True, f"Returned {len(vehicles)} vehicles with all new fields")
        return True
        
    except Exception as e:
        print_result("GET /api/vehicles", False, f"Exception: {str(e)}")
        return False

def test_vehicles_filter_new():
    """Test 2: GET /api/vehicles?condition=New - should return only New vehicles"""
    print_test_header("GET /api/vehicles?condition=New - Filter New vehicles")
    
    try:
        response = requests.get(f"{BACKEND_URL}/vehicles?condition=New", timeout=10)
        
        if response.status_code != 200:
            print_result("Filter New vehicles", False, f"Status code: {response.status_code}")
            return False
            
        vehicles = response.json()
        
        if not isinstance(vehicles, list):
            print_result("Filter New vehicles", False, "Response is not a list")
            return False
            
        # Check that all returned vehicles have condition="New"
        for vehicle in vehicles:
            if vehicle.get('condition') != 'New':
                print_result("Filter New vehicles", False, f"Vehicle {vehicle.get('stock_id')} has condition: {vehicle.get('condition')}")
                return False
                
        print_result("Filter New vehicles", True, f"Returned {len(vehicles)} New vehicles")
        return True
        
    except Exception as e:
        print_result("Filter New vehicles", False, f"Exception: {str(e)}")
        return False

def test_vehicles_filter_used():
    """Test 3: GET /api/vehicles?condition=Used - should return only Used vehicles"""
    print_test_header("GET /api/vehicles?condition=Used - Filter Used vehicles")
    
    try:
        response = requests.get(f"{BACKEND_URL}/vehicles?condition=Used", timeout=10)
        
        if response.status_code != 200:
            print_result("Filter Used vehicles", False, f"Status code: {response.status_code}")
            return False
            
        vehicles = response.json()
        
        if not isinstance(vehicles, list):
            print_result("Filter Used vehicles", False, "Response is not a list")
            return False
            
        # Check that all returned vehicles have condition="Used"
        for vehicle in vehicles:
            if vehicle.get('condition') != 'Used':
                print_result("Filter Used vehicles", False, f"Vehicle {vehicle.get('stock_id')} has condition: {vehicle.get('condition')}")
                return False
                
        print_result("Filter Used vehicles", True, f"Returned {len(vehicles)} Used vehicles")
        return True
        
    except Exception as e:
        print_result("Filter Used vehicles", False, f"Exception: {str(e)}")
        return False

def test_vehicle_detail_new():
    """Test 4: GET /api/vehicles/{stock_id} - should return New vehicle with all new fields"""
    print_test_header(f"GET /api/vehicles/{NEW_VEHICLE_STOCK} - New vehicle details")
    
    try:
        response = requests.get(f"{BACKEND_URL}/vehicles/{NEW_VEHICLE_STOCK}", timeout=10)
        
        if response.status_code != 200:
            print_result("New vehicle details", False, f"Status code: {response.status_code}")
            return False
            
        vehicle = response.json()
        
        if not isinstance(vehicle, dict):
            print_result("New vehicle details", False, "Response is not a dict")
            return False
            
        # Check specific fields for the New vehicle
        expected_fields = {
            'stock_id': NEW_VEHICLE_STOCK,
            'condition': 'New',
            'call_for_availability_enabled': True
        }
        
        for field, expected_value in expected_fields.items():
            actual_value = vehicle.get(field)
            if actual_value != expected_value:
                print_result("New vehicle details", False, f"{field}: expected {expected_value}, got {actual_value}")
                return False
                
        # Check that document URLs exist
        if not vehicle.get('carfax_url'):
            print_result("New vehicle details", False, "carfax_url is missing or empty")
            return False
            
        if not vehicle.get('window_sticker_url'):
            print_result("New vehicle details", False, "window_sticker_url is missing or empty")
            return False
            
        print_result("New vehicle details", True, f"Vehicle {NEW_VEHICLE_STOCK} has all required fields")
        return True
        
    except Exception as e:
        print_result("New vehicle details", False, f"Exception: {str(e)}")
        return False

def test_vehicle_detail_used():
    """Test 5: GET /api/vehicles/{stock_id} - should return Used vehicle"""
    print_test_header(f"GET /api/vehicles/{USED_VEHICLE_STOCK} - Used vehicle details")
    
    try:
        response = requests.get(f"{BACKEND_URL}/vehicles/{USED_VEHICLE_STOCK}", timeout=10)
        
        if response.status_code != 200:
            print_result("Used vehicle details", False, f"Status code: {response.status_code}")
            return False
            
        vehicle = response.json()
        
        if not isinstance(vehicle, dict):
            print_result("Used vehicle details", False, "Response is not a dict")
            return False
            
        # Check specific fields for the Used vehicle
        expected_fields = {
            'stock_id': USED_VEHICLE_STOCK,
            'condition': 'Used',
            'call_for_availability_enabled': False
        }
        
        for field, expected_value in expected_fields.items():
            actual_value = vehicle.get(field)
            if actual_value != expected_value:
                print_result("Used vehicle details", False, f"{field}: expected {expected_value}, got {actual_value}")
                return False
                
        print_result("Used vehicle details", True, f"Vehicle {USED_VEHICLE_STOCK} has correct fields")
        return True
        
    except Exception as e:
        print_result("Used vehicle details", False, f"Exception: {str(e)}")
        return False

def test_admin_vehicle_create():
    """Test 6: POST /api/admin/vehicles - Create vehicle with new fields"""
    print_test_header("POST /api/admin/vehicles - Create vehicle with new fields")
    
    headers = {
        'Content-Type': 'application/json',
        'x-admin-token': ADMIN_TOKEN
    }
    
    test_vehicle = {
        "vin": "TEST123456789",
        "year": 2024,
        "make": "Test",
        "model": "Vehicle",
        "trim": "Test Trim",
        "price": 25000,
        "mileage": 0,
        "condition": "New",
        "body_style": "Sedan",
        "exterior_color": "Blue",
        "interior_color": "Black",
        "carfax_url": "https://example.com/carfax",
        "window_sticker_url": "https://example.com/sticker",
        "call_for_availability_enabled": True,
        "is_active": True
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/admin/vehicles", 
                               headers=headers, 
                               json=test_vehicle, 
                               timeout=10)
        
        if response.status_code != 201:
            print_result("Create vehicle", False, f"Status code: {response.status_code}, Response: {response.text}")
            return False, None
            
        created_vehicle = response.json()
        
        # Verify all new fields are present
        for field in ['carfax_url', 'window_sticker_url', 'call_for_availability_enabled']:
            if field not in created_vehicle:
                print_result("Create vehicle", False, f"Missing field: {field}")
                return False, None
                
        vehicle_id = created_vehicle.get('id')
        print_result("Create vehicle", True, f"Created vehicle with ID: {vehicle_id}")
        return True, vehicle_id
        
    except Exception as e:
        print_result("Create vehicle", False, f"Exception: {str(e)}")
        return False, None

def test_admin_vehicle_update(vehicle_id):
    """Test 7: PATCH /api/admin/vehicles/{id} - Update vehicle with new fields"""
    print_test_header(f"PATCH /api/admin/vehicles/{vehicle_id} - Update vehicle")
    
    headers = {
        'Content-Type': 'application/json',
        'x-admin-token': ADMIN_TOKEN
    }
    
    update_data = {
        "carfax_url": "https://updated.com/carfax",
        "window_sticker_url": "https://updated.com/sticker",
        "call_for_availability_enabled": False
    }
    
    try:
        response = requests.patch(f"{BACKEND_URL}/admin/vehicles/{vehicle_id}", 
                                headers=headers, 
                                json=update_data, 
                                timeout=10)
        
        if response.status_code != 200:
            print_result("Update vehicle", False, f"Status code: {response.status_code}, Response: {response.text}")
            return False
            
        updated_vehicle = response.json()
        
        # Verify updates were applied
        for field, expected_value in update_data.items():
            actual_value = updated_vehicle.get(field)
            if actual_value != expected_value:
                print_result("Update vehicle", False, f"{field}: expected {expected_value}, got {actual_value}")
                return False
                
        print_result("Update vehicle", True, "All fields updated successfully")
        return True
        
    except Exception as e:
        print_result("Update vehicle", False, f"Exception: {str(e)}")
        return False

def test_lead_submission_availability():
    """Test 8: POST /api/vehicle-leads/availability - Create availability lead"""
    print_test_header("POST /api/vehicle-leads/availability - Create availability lead")
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    lead_data = {
        "name": "John Smith",
        "phone": "555-123-4567",
        "email": "john.smith@example.com",
        "contact_preference": "text",
        "message": "I'm interested in this vehicle's availability",
        "stock_id": NEW_VEHICLE_STOCK,
        "vin": "1HGCM82633A123456",
        "vehicle_summary": "2025 Honda Accord"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/vehicle-leads/availability", 
                               headers=headers, 
                               json=lead_data, 
                               timeout=10)
        
        if response.status_code != 200:
            print_result("Create availability lead", False, f"Status code: {response.status_code}, Response: {response.text}")
            return False, None
            
        created_lead = response.json()
        
        # Verify lead was created with correct type
        lead_id = created_lead.get('id')
        if not lead_id:
            print_result("Create availability lead", False, "No lead ID returned")
            return False, None
            
        print_result("Create availability lead", True, f"Created lead with ID: {lead_id}")
        return True, lead_id
        
    except Exception as e:
        print_result("Create availability lead", False, f"Exception: {str(e)}")
        return False, None

def test_lead_submission_form():
    """Test 9: POST /api/vehicle-leads - Create form lead with availability type"""
    print_test_header("POST /api/vehicle-leads - Create form lead")
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    lead_data = {
        "type": "availability",
        "firstName": "Jane",
        "lastName": "Doe",
        "phone": "555-987-6543",
        "email": "jane.doe@example.com",
        "stockNumber": NEW_VEHICLE_STOCK,
        "source": "vehicle-detail-page",
        "notes": "Interested in availability and pricing"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/vehicle-leads", 
                               headers=headers, 
                               json=lead_data, 
                               timeout=10)
        
        if response.status_code != 200:
            print_result("Create form lead", False, f"Status code: {response.status_code}, Response: {response.text}")
            return False, None
            
        result = response.json()
        
        if not result.get('ok'):
            print_result("Create form lead", False, f"API returned ok=false: {result}")
            return False, None
            
        lead_id = result.get('id')
        print_result("Create form lead", True, f"Created form lead with ID: {lead_id}")
        return True, lead_id
        
    except Exception as e:
        print_result("Create form lead", False, f"Exception: {str(e)}")
        return False, None

def verify_lead_in_database(lead_id):
    """Test 10: Verify lead is stored correctly in MongoDB via admin API"""
    print_test_header(f"GET /api/leads/{lead_id} - Verify lead storage")
    
    headers = {
        'x-admin-token': ADMIN_TOKEN
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}/leads/{lead_id}", 
                              headers=headers, 
                              timeout=10)
        
        if response.status_code != 200:
            print_result("Verify lead storage", False, f"Status code: {response.status_code}")
            return False
            
        lead = response.json()
        
        # Verify lead has correct type
        if lead.get('lead_type') != 'availability':
            print_result("Verify lead storage", False, f"Expected lead_type 'availability', got '{lead.get('lead_type')}'")
            return False
            
        print_result("Verify lead storage", True, f"Lead stored with correct type: {lead.get('lead_type')}")
        return True
        
    except Exception as e:
        print_result("Verify lead storage", False, f"Exception: {str(e)}")
        return False

def test_featured_vehicles_endpoint():
    """Test 11: GET /api/vehicles/featured - should return only featured vehicles"""
    print_test_header("GET /api/vehicles/featured - Featured vehicles endpoint")
    
    try:
        response = requests.get(f"{BACKEND_URL}/vehicles/featured?limit=8", timeout=10)
        
        if response.status_code != 200:
            print_result("Featured vehicles endpoint", False, f"Status code: {response.status_code}")
            return False
            
        vehicles = response.json()
        
        if not isinstance(vehicles, list):
            print_result("Featured vehicles endpoint", False, "Response is not a list")
            return False
            
        # Check that all returned vehicles have is_featured_homepage=true
        for vehicle in vehicles:
            if not vehicle.get('is_featured_homepage'):
                print_result("Featured vehicles endpoint", False, f"Vehicle {vehicle.get('stock_id')} is not featured")
                return False
                
            # Check required fields are present
            required_fields = ['is_featured_homepage', 'featured_rank', 'primary_image_url', 'price', 'mileage']
            for field in required_fields:
                if field not in vehicle:
                    print_result("Featured vehicles endpoint", False, f"Missing field: {field}")
                    return False
                    
        print_result("Featured vehicles endpoint", True, f"Returned {len(vehicles)} featured vehicles with all required fields")
        return True
        
    except Exception as e:
        print_result("Featured vehicles endpoint", False, f"Exception: {str(e)}")
        return False

def test_update_vehicle_featured_status():
    """Test 12: PATCH /api/admin/vehicles/{id} - Update vehicle featured status"""
    print_test_header("PATCH /api/admin/vehicles/{id} - Update featured status")
    
    headers = {
        'Content-Type': 'application/json',
        'x-admin-token': ADMIN_TOKEN
    }
    
    # First, get a non-featured vehicle to update
    try:
        response = requests.get(f"{BACKEND_URL}/vehicles", timeout=10)
        if response.status_code != 200:
            print_result("Update featured status", False, "Could not get vehicles list")
            return False, None
            
        vehicles = response.json()
        non_featured_vehicle = None
        
        for vehicle in vehicles:
            if not vehicle.get('is_featured_homepage', False):
                non_featured_vehicle = vehicle
                break
                
        if not non_featured_vehicle:
            print_result("Update featured status", False, "No non-featured vehicle found to test with")
            return False, None
            
        vehicle_id = non_featured_vehicle['id']
        
        # Update vehicle to be featured
        update_data = {
            "is_featured_homepage": True,
            "featured_rank": 99
        }
        
        response = requests.patch(f"{BACKEND_URL}/admin/vehicles/{vehicle_id}", 
                                headers=headers, 
                                json=update_data, 
                                timeout=10)
        
        if response.status_code != 200:
            print_result("Update featured status", False, f"Status code: {response.status_code}, Response: {response.text}")
            return False, None
            
        updated_vehicle = response.json()
        
        # Verify updates were applied
        if not updated_vehicle.get('is_featured_homepage'):
            print_result("Update featured status", False, "is_featured_homepage not set to true")
            return False, None
            
        if updated_vehicle.get('featured_rank') != 99:
            print_result("Update featured status", False, f"featured_rank: expected 99, got {updated_vehicle.get('featured_rank')}")
            return False, None
            
        print_result("Update featured status", True, f"Vehicle {vehicle_id} successfully updated to featured")
        return True, vehicle_id
        
    except Exception as e:
        print_result("Update featured status", False, f"Exception: {str(e)}")
        return False, None

def test_featured_vehicles_order():
    """Test 13: Verify featured vehicles are sorted by featured_rank"""
    print_test_header("Featured vehicles sorting by rank")
    
    try:
        response = requests.get(f"{BACKEND_URL}/vehicles/featured?limit=8", timeout=10)
        
        if response.status_code != 200:
            print_result("Featured vehicles sorting", False, f"Status code: {response.status_code}")
            return False
            
        vehicles = response.json()
        
        if len(vehicles) < 2:
            print_result("Featured vehicles sorting", True, "Less than 2 vehicles, sorting test not applicable")
            return True
            
        # Check that vehicles are sorted by featured_rank (nulls last)
        prev_rank = None
        for vehicle in vehicles:
            current_rank = vehicle.get('featured_rank')
            
            if prev_rank is not None and current_rank is not None:
                if current_rank < prev_rank:
                    print_result("Featured vehicles sorting", False, f"Vehicles not sorted by rank: {prev_rank} -> {current_rank}")
                    return False
                    
            prev_rank = current_rank
            
        print_result("Featured vehicles sorting", True, "Vehicles properly sorted by featured_rank")
        return True
        
    except Exception as e:
        print_result("Featured vehicles sorting", False, f"Exception: {str(e)}")
        return False

def test_remove_from_featured():
    """Test 14: Remove vehicle from featured list"""
    print_test_header("Remove vehicle from featured list")
    
    headers = {
        'Content-Type': 'application/json',
        'x-admin-token': ADMIN_TOKEN
    }
    
    try:
        # Get featured vehicles first
        response = requests.get(f"{BACKEND_URL}/vehicles/featured?limit=8", timeout=10)
        if response.status_code != 200:
            print_result("Remove from featured", False, "Could not get featured vehicles")
            return False
            
        featured_vehicles = response.json()
        if len(featured_vehicles) == 0:
            print_result("Remove from featured", False, "No featured vehicles to test with")
            return False
            
        # Pick the first featured vehicle to remove
        vehicle_to_remove = featured_vehicles[0]
        vehicle_id = vehicle_to_remove['id']
        
        # Update vehicle to remove from featured
        update_data = {
            "is_featured_homepage": False,
            "featured_rank": None
        }
        
        response = requests.patch(f"{BACKEND_URL}/admin/vehicles/{vehicle_id}", 
                                headers=headers, 
                                json=update_data, 
                                timeout=10)
        
        if response.status_code != 200:
            print_result("Remove from featured", False, f"Status code: {response.status_code}")
            return False
            
        # Verify it no longer appears in featured list
        response = requests.get(f"{BACKEND_URL}/vehicles/featured?limit=8", timeout=10)
        if response.status_code != 200:
            print_result("Remove from featured", False, "Could not verify removal")
            return False
            
        updated_featured = response.json()
        
        # Check that the vehicle is no longer in the featured list
        for vehicle in updated_featured:
            if vehicle['id'] == vehicle_id:
                print_result("Remove from featured", False, "Vehicle still appears in featured list")
                return False
                
        print_result("Remove from featured", True, f"Vehicle {vehicle_id} successfully removed from featured")
        return True
        
    except Exception as e:
        print_result("Remove from featured", False, f"Exception: {str(e)}")
        return False

def cleanup_test_vehicle(vehicle_id):
    """Clean up test vehicle"""
    if not vehicle_id:
        return
        
    headers = {
        'x-admin-token': ADMIN_TOKEN
    }
    
    try:
        response = requests.delete(f"{BACKEND_URL}/admin/vehicles/{vehicle_id}", 
                                 headers=headers, 
                                 timeout=10)
        if response.status_code == 200:
            print(f"✅ Cleaned up test vehicle: {vehicle_id}")
        else:
            print(f"⚠️ Failed to clean up test vehicle: {vehicle_id}")
    except Exception as e:
        print(f"⚠️ Error cleaning up test vehicle: {str(e)}")

def cleanup_featured_test_vehicle(vehicle_id):
    """Clean up featured test vehicle by removing from featured"""
    if not vehicle_id:
        return
        
    headers = {
        'Content-Type': 'application/json',
        'x-admin-token': ADMIN_TOKEN
    }
    
    try:
        # Remove from featured instead of deleting
        update_data = {
            "is_featured_homepage": False,
            "featured_rank": None
        }
        
        response = requests.patch(f"{BACKEND_URL}/admin/vehicles/{vehicle_id}", 
                                headers=headers, 
                                json=update_data, 
                                timeout=10)
        if response.status_code == 200:
            print(f"✅ Cleaned up featured test vehicle: {vehicle_id}")
        else:
            print(f"⚠️ Failed to clean up featured test vehicle: {vehicle_id}")
    except Exception as e:
        print(f"⚠️ Error cleaning up featured test vehicle: {str(e)}")

def main():
    """Run all backend tests for Vehicle Image Pipeline"""
    print("🚗 Choose Me Auto - Vehicle Image Pipeline Testing")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    test_vehicle_id = None
    
    # IMG-1: Upload Flow Test
    img1_success, test_vehicle_id = test_img1_upload_flow()
    test_results.append(img1_success)
    
    if not test_vehicle_id:
        print("\n❌ Cannot continue tests without a test vehicle")
        return False
    
    # IMG-2: Image Data Contract Test
    test_results.append(test_img2_data_contract(test_vehicle_id))
    
    # IMG-3: Migration Test
    test_results.append(test_img3_migration())
    
    # IMG-5: Validation Test
    test_results.append(test_img5_validation(test_vehicle_id))
    
    # IMG-6: Delete Photo Test
    test_results.append(test_img6_delete_photo(test_vehicle_id))
    
    # IMG-7: Set Primary Photo Test
    test_results.append(test_img7_set_primary(test_vehicle_id))
    
    # Clean up test vehicle
    if test_vehicle_id:
        cleanup_test_vehicle(test_vehicle_id)
    
    # Summary
    print(f"\n{'='*60}")
    print("VEHICLE IMAGE PIPELINE TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(test_results)
    total = len(test_results)
    
    test_names = [
        "IMG-1: Upload Flow Test",
        "IMG-2: Image Data Contract Test", 
        "IMG-3: Migration Test",
        "IMG-5: Validation Test",
        "IMG-6: Delete Photo Test",
        "IMG-7: Set Primary Photo Test"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, test_results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Vehicle Image Pipeline tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check the details above.")
        return False

def cleanup_test_vehicle(vehicle_id):
    """Clean up test vehicle"""
    if not vehicle_id:
        return
        
    headers = {
        'x-admin-token': ADMIN_TOKEN
    }
    
    try:
        response = requests.delete(f"{BACKEND_URL}/admin/vehicles/{vehicle_id}", 
                                 headers=headers, 
                                 timeout=10)
        if response.status_code == 200:
            print(f"✅ Cleaned up test vehicle: {vehicle_id}")
        else:
            print(f"⚠️ Failed to clean up test vehicle: {vehicle_id}")
    except Exception as e:
        print(f"⚠️ Error cleaning up test vehicle: {str(e)}")

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)