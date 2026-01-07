#!/usr/bin/env python3
"""
Backend API Testing for Choose Me Auto Car Dealership
Tests the newly implemented features as specified in the review request.
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://autodealership.preview.emergentagent.com/api"
ADMIN_TOKEN = "cma-admin-2c8e1cd0f9b70c27827d310304fd7b4c"

# Test data
NEW_VEHICLE_STOCK = "CMAEE34F7"  # 2025 Honda Accord
USED_VEHICLE_STOCK = "CMA5A1BBF"  # 2023 Toyota Camry

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"TESTING: {test_name}")
    print(f"{'='*60}")

def print_result(test_name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   Details: {details}")

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
        return True, vehicles
        
    except Exception as e:
        print_result("Featured vehicles endpoint", False, f"Exception: {str(e)}")
        return False, []

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
    """Run all backend tests"""
    print("🚗 Choose Me Auto - Backend API Testing")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    test_vehicle_id = None
    
    # Test 1: Get all vehicles
    test_results.append(test_vehicles_api())
    
    # Test 2: Filter New vehicles
    test_results.append(test_vehicles_filter_new())
    
    # Test 3: Filter Used vehicles
    test_results.append(test_vehicles_filter_used())
    
    # Test 4: Get New vehicle details
    test_results.append(test_vehicle_detail_new())
    
    # Test 5: Get Used vehicle details
    test_results.append(test_vehicle_detail_used())
    
    # Test 6: Create vehicle with new fields
    create_success, test_vehicle_id = test_admin_vehicle_create()
    test_results.append(create_success)
    
    # Test 7: Update vehicle (only if create succeeded)
    if create_success and test_vehicle_id:
        test_results.append(test_admin_vehicle_update(test_vehicle_id))
    else:
        test_results.append(False)
    
    # Test 8: Create availability lead (legacy endpoint)
    lead_success, lead_id = test_lead_submission_availability()
    test_results.append(lead_success)
    
    # Test 9: Create form lead
    form_lead_success, form_lead_id = test_lead_submission_form()
    test_results.append(form_lead_success)
    
    # Test 10: Verify lead storage (use whichever lead was created successfully)
    verification_lead_id = lead_id if lead_success else form_lead_id
    if verification_lead_id:
        test_results.append(verify_lead_in_database(verification_lead_id))
    else:
        test_results.append(False)
    
    # Clean up test vehicle
    cleanup_test_vehicle(test_vehicle_id)
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(test_results)
    total = len(test_results)
    
    test_names = [
        "GET /api/vehicles",
        "Filter New vehicles",
        "Filter Used vehicles", 
        "New vehicle details",
        "Used vehicle details",
        "Create vehicle",
        "Update vehicle",
        "Create availability lead",
        "Create form lead",
        "Verify lead storage"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, test_results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check the details above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)