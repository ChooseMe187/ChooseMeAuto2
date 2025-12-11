from fastapi import Header, HTTPException, status
import os

# Simple admin token authentication
# In production, use a proper auth system (JWT, OAuth, etc.)
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "choosemeauto-admin-2024")

async def require_admin(x_admin_token: str = Header(None)):
    """Simple admin authentication via header token"""
    if not x_admin_token or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin token"
        )
    return True


async def verify_admin_login(password: str) -> bool:
    """Verify admin login credentials"""
    admin_password = os.environ.get("ADMIN_PASSWORD", "chooseme2024")
    return password == admin_password
