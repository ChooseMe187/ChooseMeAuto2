"""
Admin Authentication Module with Rate Limiting

Security features:
- Token-based API authentication
- Password-based login with rate limiting
- Lockout after failed attempts
"""
from fastapi import Header, HTTPException, status, Request
import os
import time
from datetime import datetime, timezone
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# Configuration from environment
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "choosemeauto-admin-default")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "chooseme2024-default")
MAX_LOGIN_ATTEMPTS = int(os.environ.get("MAX_LOGIN_ATTEMPTS", "5"))
LOGIN_LOCKOUT_MINUTES = int(os.environ.get("LOGIN_LOCKOUT_MINUTES", "15"))

# In-memory rate limiting (for single instance)
# For multi-instance deployments, use Redis
_login_attempts = defaultdict(list)  # IP -> list of timestamps
_locked_ips = {}  # IP -> lockout_until timestamp


def _get_client_ip(request: Request = None) -> str:
    """Extract client IP from request"""
    if not request:
        return "unknown"
    
    # Check for forwarded headers (when behind proxy)
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"


def _is_locked_out(ip: str) -> bool:
    """Check if IP is currently locked out"""
    if ip in _locked_ips:
        if time.time() < _locked_ips[ip]:
            return True
        else:
            # Lockout expired, remove it
            del _locked_ips[ip]
            _login_attempts.pop(ip, None)
    return False


def _record_failed_attempt(ip: str) -> int:
    """Record a failed login attempt, return remaining attempts"""
    now = time.time()
    cutoff = now - (LOGIN_LOCKOUT_MINUTES * 60)
    
    # Clean old attempts
    _login_attempts[ip] = [t for t in _login_attempts[ip] if t > cutoff]
    
    # Add new attempt
    _login_attempts[ip].append(now)
    
    attempts = len(_login_attempts[ip])
    remaining = MAX_LOGIN_ATTEMPTS - attempts
    
    # Check if should lockout
    if attempts >= MAX_LOGIN_ATTEMPTS:
        _locked_ips[ip] = now + (LOGIN_LOCKOUT_MINUTES * 60)
        logger.warning(f"IP {ip} locked out for {LOGIN_LOCKOUT_MINUTES} minutes after {attempts} failed attempts")
    
    return max(0, remaining)


def _clear_attempts(ip: str):
    """Clear login attempts on successful login"""
    _login_attempts.pop(ip, None)
    _locked_ips.pop(ip, None)


async def require_admin(x_admin_token: str = Header(None)):
    """
    Admin authentication via header token.
    
    Usage:
        @router.get("/admin/resource")
        async def protected_route(_: bool = Depends(require_admin)):
            ...
    """
    if not x_admin_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing admin token. Include 'x-admin-token' header."
        )
    
    if x_admin_token != ADMIN_TOKEN:
        logger.warning(f"Invalid admin token attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token"
        )
    
    return True


async def verify_admin_login(password: str, request: Request = None) -> dict:
    """
    Verify admin login credentials with rate limiting.
    
    Returns:
        dict with keys: success, message, remaining_attempts (on failure)
    """
    ip = _get_client_ip(request)
    
    # Check lockout
    if _is_locked_out(ip):
        lockout_remaining = int(_locked_ips.get(ip, 0) - time.time())
        minutes = max(1, lockout_remaining // 60)
        logger.warning(f"Login attempt from locked IP: {ip}")
        return {
            "success": False,
            "message": f"Too many failed attempts. Try again in {minutes} minute(s).",
            "locked": True,
            "lockout_minutes": minutes
        }
    
    # Verify password
    if password == ADMIN_PASSWORD:
        _clear_attempts(ip)
        logger.info(f"Successful admin login from {ip}")
        return {
            "success": True,
            "message": "Login successful"
        }
    else:
        remaining = _record_failed_attempt(ip)
        logger.warning(f"Failed admin login from {ip}. Remaining attempts: {remaining}")
        
        if remaining > 0:
            return {
                "success": False,
                "message": f"Invalid password. {remaining} attempt(s) remaining.",
                "remaining_attempts": remaining
            }
        else:
            return {
                "success": False,
                "message": f"Too many failed attempts. Account locked for {LOGIN_LOCKOUT_MINUTES} minutes.",
                "locked": True,
                "lockout_minutes": LOGIN_LOCKOUT_MINUTES
            }


# Legacy function for backward compatibility
async def verify_admin_login_simple(password: str) -> bool:
    """Simple password verification (no rate limiting)"""
    return password == ADMIN_PASSWORD


def get_security_status() -> dict:
    """Get current security status for monitoring"""
    return {
        "max_login_attempts": MAX_LOGIN_ATTEMPTS,
        "lockout_minutes": LOGIN_LOCKOUT_MINUTES,
        "currently_locked_ips": len(_locked_ips),
        "tracked_ips": len(_login_attempts),
    }
