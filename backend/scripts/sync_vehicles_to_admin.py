"""
Migration script to sync vehicles from public API to admin_vehicles collection.

This script:
1. Fetches all vehicles from the public API
2. Inserts/updates them in the admin_vehicles collection
3. Preserves existing admin_vehicles data

Run with: python3 sync_vehicles_to_admin.py
"""
import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import httpx

# Configuration
API_BASE = os.environ.get("API_BASE", "https://choosemeauto.com")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")


async def fetch_public_vehicles():
    """Fetch all vehicles from the public API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/api/vehicles", timeout=30)
        response.raise_for_status()
        return response.json()


async def sync_to_admin_collection(vehicles: list, db):
    """Sync vehicles to admin_vehicles collection."""
    collection = db["admin_vehicles"]
    
    created = 0
    updated = 0
    skipped = 0
    
    for vehicle in vehicles:
        # Use stock_id or id as the unique identifier
        stock_id = vehicle.get("stock_id") or vehicle.get("id")
        vin = vehicle.get("vin", "")
        
        if not stock_id:
            print(f"  ⚠️ Skipping vehicle without stock_id: {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}")
            skipped += 1
            continue
        
        # Check if vehicle already exists
        existing = await collection.find_one({
            "$or": [
                {"stock_number": stock_id},
                {"vin": vin} if vin else {"_id": None}
            ]
        })
        
        # Prepare document for admin collection
        doc = {
            "stock_number": stock_id,
            "vin": vin,
            "year": vehicle.get("year"),
            "make": vehicle.get("make"),
            "model": vehicle.get("model"),
            "trim": vehicle.get("trim", ""),
            "price": vehicle.get("price"),
            "mileage": vehicle.get("mileage"),
            "condition": vehicle.get("condition", "Used"),
            "body_style": vehicle.get("body_style", ""),
            "exterior_color": vehicle.get("exterior_color", ""),
            "interior_color": vehicle.get("interior_color", ""),
            "transmission": vehicle.get("transmission", ""),
            "drivetrain": vehicle.get("drivetrain", ""),
            "fuel_type": vehicle.get("fuel_type", ""),
            "engine": vehicle.get("engine", ""),
            "is_active": True,
            "is_featured_homepage": vehicle.get("is_featured_homepage", False),
            "featured_rank": vehicle.get("featured_rank"),
            "updated_at": datetime.now(timezone.utc),
        }
        
        # Handle images
        if vehicle.get("images"):
            doc["images"] = vehicle["images"]
        elif vehicle.get("primary_image_url"):
            doc["images"] = [{"url": vehicle["primary_image_url"], "is_primary": True}]
        
        if existing:
            # Update existing
            await collection.update_one(
                {"_id": existing["_id"]},
                {"$set": doc}
            )
            updated += 1
            print(f"  🔄 Updated: {stock_id} - {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}")
        else:
            # Insert new
            doc["created_at"] = datetime.now(timezone.utc)
            await collection.insert_one(doc)
            created += 1
            print(f"  ✅ Created: {stock_id} - {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}")
    
    return created, updated, skipped


async def main():
    print("=" * 50)
    print("  Vehicle Sync: Public API → Admin Collection")
    print("=" * 50)
    
    # Connect to MongoDB
    print(f"\n📦 Connecting to MongoDB: {MONGO_URL[:50]}...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    print(f"📦 Using database: {DB_NAME}")
    
    # Test connection
    try:
        await client.admin.command('ping')
        print("✅ MongoDB connection verified")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        sys.exit(1)
    
    # Check current admin_vehicles count
    admin_count = await db["admin_vehicles"].count_documents({})
    print(f"\n📊 Current admin_vehicles count: {admin_count}")
    
    # Fetch public vehicles
    print(f"\n🌐 Fetching vehicles from {API_BASE}/api/vehicles...")
    try:
        vehicles = await fetch_public_vehicles()
        print(f"📥 Fetched {len(vehicles)} vehicles from public API")
    except Exception as e:
        print(f"❌ Failed to fetch vehicles: {e}")
        sys.exit(1)
    
    if not vehicles:
        print("⚠️ No vehicles found in public API")
        sys.exit(0)
    
    # Sync to admin collection
    print(f"\n🔄 Syncing to admin_vehicles collection...")
    created, updated, skipped = await sync_to_admin_collection(vehicles, db)
    
    # Final count
    final_count = await db["admin_vehicles"].count_documents({})
    
    print("\n" + "=" * 50)
    print("  SYNC COMPLETE")
    print("=" * 50)
    print(f"  ✅ Created: {created}")
    print(f"  🔄 Updated: {updated}")
    print(f"  ⚠️ Skipped: {skipped}")
    print(f"  📊 Total in admin_vehicles: {final_count}")
    print("=" * 50)
    
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
