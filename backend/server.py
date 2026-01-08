from fastapi import FastAPI, APIRouter, Request
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from pathlib import Path
import time

# Load environment variables FIRST before any imports that use them
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routers and services AFTER loading env
from routes.vehicles import router as vehicles_router, set_db as set_vehicles_db
from routes.leads import router as leads_router, set_db as set_leads_db
from routes.admin_vehicles import router as admin_router, set_db as set_admin_db
from utils.alerts import get_notification_status


# Request logging middleware for observability
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log request details (excluding sensitive paths in detail)
        path = request.url.path
        method = request.method
        status = response.status_code
        
        # Don't log health checks to reduce noise
        if path not in ["/health", "/api/health", "/"]:
            # Log auth failures without credentials
            if status == 401 or (path == "/api/admin/login" and status != 200):
                logger.warning(f"AUTH_FAILURE: {method} {path} - {status} - {process_time:.3f}s")
            elif status >= 400:
                logger.warning(f"REQUEST: {method} {path} - {status} - {process_time:.3f}s")
            else:
                logger.info(f"REQUEST: {method} {path} - {status} - {process_time:.3f}s")
        
        return response

# MongoDB connection with error handling
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'test_database')

logger.info(f"Connecting to MongoDB at: {mongo_url[:30]}...")
logger.info(f"Using database: {db_name}")

try:
    client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
    db = client[db_name]
    logger.info("MongoDB client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MongoDB client: {e}")
    raise

# Application version info
APP_VERSION = "2.0.0"
BUILD_DATE = "2025-01"

# Create the main app without a prefix
app = FastAPI(title="Choose Me Auto API", version=APP_VERSION)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str


# Health check endpoint - CRITICAL for Kubernetes
@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes liveness/readiness probes"""
    try:
        # Try to ping MongoDB to verify connection
        await client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# API-prefixed health check (for ingress routing)
@api_router.get("/health")
async def api_health_check():
    """Health check endpoint under /api prefix"""
    try:
        await client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Root health check (backup)
@app.get("/")
async def root_health():
    """Root endpoint - also used for health checks"""
    return {"status": "ok", "service": "Choose Me Auto API"}


# Add your routes to the router instead of directly to app
@api_router.get("/")
async def api_root():
    return {"message": "Choose Me Auto API", "version": APP_VERSION}


@api_router.get("/version")
async def api_version():
    """
    Returns build/version info for observability.
    Useful for verifying deployments and debugging.
    """
    return {
        "version": APP_VERSION,
        "build_date": BUILD_DATE,
        "service": "Choose Me Auto API",
        "environment": os.environ.get("ENVIRONMENT", "development"),
    }


@api_router.get("/notifications/status")
async def notifications_status():
    """
    Get the current status of all notification channels.
    Phase 2B Status:
    - Phase 2B.1 – Email Architecture: ✅ Complete
    - Phase 2B.2 – Email Provider Activation: ⏸ Deferred (external dependency)
    """
    status = get_notification_status()
    status["phase"] = {
        "2B.1_email_architecture": "complete",
        "2B.2_email_provider": "deferred"
    }
    return status


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks


# Include the routers in the main app
app.include_router(api_router)
app.include_router(vehicles_router, prefix="/api")
app.include_router(leads_router, prefix="/api")
app.include_router(admin_router)  # Admin router has its own /api/admin prefix

# Set database for admin routes
set_admin_db(db)

# Set database for leads routes
set_leads_db(db)

# Set database for vehicles routes
set_vehicles_db(db)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Application startup - verify MongoDB connection"""
    logger.info("Application starting up...")
    try:
        await client.admin.command('ping')
        logger.info("✅ MongoDB connection verified")
    except Exception as e:
        logger.warning(f"⚠️ MongoDB ping failed on startup: {e}")
        # Don't crash - let the health check handle it


@app.on_event("shutdown")
async def shutdown_db_client():
    """Clean shutdown - close MongoDB connection"""
    logger.info("Application shutting down...")
    client.close()
    logger.info("MongoDB connection closed")
