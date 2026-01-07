#!/usr/bin/env python3
"""
Backend API Testing for Choose Me Auto Car Dealership
Tests the Security & Performance Updates as specified in the review request.
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

# Security Test Credentials
OLD_ADMIN_TOKEN = "cma-admin-2c8e1cd0f9b70c27827d310304fd7b4c"  # Should be rejected
NEW_ADMIN_TOKEN = "cma-admin-020f6b7ada4b976c76f6b2bd02cffe5cb08509e6ad2d22e2"  # Should work
NEW_ADMIN_PASSWORD = "CMA_38d5c79bbdb6b28d95c0938dc0a844f6"

# Test data
TEST_VEHICLE_STOCK = "CMASEC001"  # Security test vehicle

def create_test_image(width=800, height=600, format='JPEG', color=(255, 0, 0)):
    """Create a test image in memory"""
    img = Image.new('RGB', (width, height), color)
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)
    return buffer.getvalue()

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"TESTING: {test_name}")
    print(f"{'='*60}")

def print_result(test_name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   Details: {details}")

# S0.1: Credential Rotation Test
def test_s01_credential_rotation():
def test_s01_credential_rotation():
    """S0.1: Test credential rotation and rate limiting"""
    print_test_header("S0.1: Credential Rotation Test")
    
    # Test 1: OLD token should be rejected
    try:
        headers = {'x-admin-token': OLD_ADMIN_TOKEN}
        response = requests.get(f"{BACKEND_URL}/admin/vehicles", headers=headers, timeout=10)
        
        if response.status_code == 401:
            print_result("OLD token rejection", True, "Old token properly rejected with 401")
        else:
            print_result("OLD token rejection", False, f"Expected 401, got {response.status_code}")
            return False
    except Exception as e:
        print_result("OLD token rejection", False, f"Exception: {str(e)}")
        return False
    
    # Test 2: NEW token should work
    try:
        headers = {'x-admin-token': NEW_ADMIN_TOKEN}
        response = requests.get(f"{BACKEND_URL}/admin/vehicles", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print_result("NEW token acceptance", True, "New token works correctly")
        else:
            print_result("NEW token acceptance", False, f"Expected 200, got {response.status_code}")
            return False
    except Exception as e:
        print_result("NEW token acceptance", False, f"Exception: {str(e)}")
        return False
    
    # Test 3: Login rate limiting
    try:
        wrong_password = "wrong_password_123"
        login_data = {"password": wrong_password}
        
        # Make 3 failed attempts
        for i in range(3):
            response = requests.post(f"{BACKEND_URL}/admin/login", 
                                   json=login_data, 
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if not result.get("success", True):
                    remaining = result.get("remaining_attempts")
                    if remaining is not None:
                        print_result(f"Failed attempt {i+1}", True, f"Remaining attempts: {remaining}")
                    else:
                        print_result(f"Failed attempt {i+1}", True, "Login failed as expected")
                else:
                    print_result(f"Failed attempt {i+1}", False, "Login should have failed")
                    return False
            else:
                print_result(f"Failed attempt {i+1}", False, f"Unexpected status: {response.status_code}")
                return False
        
        print_result("S0.1: Credential Rotation", True, "All credential tests passed")
        return True
        
    except Exception as e:
        print_result("S0.1: Credential Rotation", False, f"Rate limiting test exception: {str(e)}")
        return False


# S0.2: Upload Limit Test
def test_s02_upload_limits():
    """S0.2: Test upload payload limits"""
    print_test_header("S0.2: Upload Limit Test")
    
    # First, create a test vehicle
    headers = {
        'Content-Type': 'application/json',
        'x-admin-token': NEW_ADMIN_TOKEN
    }
    
    test_vehicle = {
        "vin": "S02TEST123456789",
        "year": 2024,
        "make": "Test",
        "model": "UploadLimit",
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
        
        # Test: Try to upload more than 12 images (should fail)
        test_images = []
        for i in range(13):  # 13 images (exceeds limit of 12)
            test_image = create_test_image(format='JPEG', color=(i*20, 100, 200))
            test_images.append(('files', (f'test{i}.jpg', test_image, 'image/jpeg')))
        
        upload_headers = {'x-admin-token': NEW_ADMIN_TOKEN}
        
        response = requests.post(f"{BACKEND_URL}/admin/vehicles/{vehicle_id}/photos",
                               headers=upload_headers,
                               files=test_images,
                               timeout=30)
        
        if response.status_code == 400:
            result = response.json()
            if "limit exceeded" in str(result).lower() or "maximum" in str(result).lower():
                print_result("Upload limit enforcement", True, "Upload limit properly enforced")
                return True, vehicle_id
            else:
                print_result("Upload limit enforcement", False, f"Wrong error message: {result}")
                return False, vehicle_id
        else:
            print_result("Upload limit enforcement", False, f"Expected 400, got {response.status_code}")
            return False, vehicle_id
            
    except Exception as e:
        print_result("S0.2: Upload Limits", False, f"Exception: {str(e)}")
        return False, None


# S0.3: API Response Optimization Test
def test_s03_api_optimization():
    """S0.3: Test API response optimization"""
    print_test_header("S0.3: API Response Optimization Test")
    
    try:
        # Test 1: GET /api/vehicles (list) - should have limited fields
        response = requests.get(f"{BACKEND_URL}/vehicles", timeout=10)
        
        if response.status_code != 200:
            print_result("Vehicles list endpoint", False, f"Status code: {response.status_code}")
            return False
            
        vehicles_list = response.json()
        
        if not vehicles_list:
            print_result("Vehicles list data", False, "No vehicles found for testing")
            return False
        
        # Check first vehicle in list
        first_vehicle = vehicles_list[0]
        
        # Required fields for list view
        required_list_fields = [
            'stock_id', 'id', 'vin', 'year', 'make', 'model', 'trim', 
            'price', 'mileage', 'primary_image_url', 'body_style', 'condition'
        ]
        
        # Fields that should NOT be in list view
        excluded_list_fields = ['images', 'photo_urls', 'carfax_url', 'drivetrain']
        
        # Check required fields are present
        missing_fields = []
        for field in required_list_fields:
            if field not in first_vehicle:
                missing_fields.append(field)
        
        if missing_fields:
            print_result("List view required fields", False, f"Missing fields: {missing_fields}")
            return False
        
        # Check excluded fields are absent
        present_excluded = []
        for field in excluded_list_fields:
            if field in first_vehicle:
                present_excluded.append(field)
        
        if present_excluded:
            print_result("List view excluded fields", False, f"Should not have: {present_excluded}")
            return False
        
        print_result("List view optimization", True, "List endpoint properly optimized")
        
        # Test 2: GET /api/vehicles/{stock_id} (detail) - should have all fields
        stock_id = first_vehicle.get('stock_id')
        if not stock_id:
            print_result("Stock ID for detail test", False, "No stock_id found")
            return False
        
        response = requests.get(f"{BACKEND_URL}/vehicles/{stock_id}", timeout=10)
        
        if response.status_code != 200:
            print_result("Vehicle detail endpoint", False, f"Status code: {response.status_code}")
            return False
            
        vehicle_detail = response.json()
        
        # Required fields for detail view (includes all list fields plus extras)
        required_detail_fields = required_list_fields + [
            'images', 'photo_urls', 'carfax_url', 'window_sticker_url',
            'drivetrain', 'exterior_color', 'interior_color'
        ]
        
        # Check all required fields are present
        missing_detail_fields = []
        for field in required_detail_fields:
            if field not in vehicle_detail:
                missing_detail_fields.append(field)
        
        if missing_detail_fields:
            print_result("Detail view required fields", False, f"Missing fields: {missing_detail_fields}")
            return False
        
        print_result("Detail view completeness", True, "Detail endpoint has all required fields")
        print_result("S0.3: API Optimization", True, "API response optimization working correctly")
        return True
        
    except Exception as e:
        print_result("S0.3: API Optimization", False, f"Exception: {str(e)}")
        return False


def cleanup_test_vehicle(vehicle_id):
    """Clean up test vehicle"""
    if not vehicle_id:
        return
        
    headers = {
        'x-admin-token': NEW_ADMIN_TOKEN
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


def main():
    """Run all backend tests for Security & Performance Updates"""
    print("🔒 Choose Me Auto - Security & Performance Testing")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    test_vehicle_id = None
    
    # S0.1: Credential Rotation Test
    test_results.append(test_s01_credential_rotation())
    
    # S0.2: Upload Limit Test
    s02_success, test_vehicle_id = test_s02_upload_limits()
    test_results.append(s02_success)
    
    # S0.3: API Response Optimization Test
    test_results.append(test_s03_api_optimization())
    
    # Clean up test vehicle
    if test_vehicle_id:
        cleanup_test_vehicle(test_vehicle_id)
    
    # Summary
    print(f"\n{'='*60}")
    print("SECURITY & PERFORMANCE TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(test_results)
    total = len(test_results)
    
    test_names = [
        "S0.1: Credential Rotation Test",
        "S0.2: Upload Limit Test", 
        "S0.3: API Response Optimization Test"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, test_results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Security & Performance tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check the details above.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)