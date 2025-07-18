import os
import secrets
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from functools import wraps
import asyncio
from fastapi import HTTPException, Request, status
from fastapi.security import APIKeyHeader
from .database import get_database

# API Key header configuration
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Rate limit configuration
RATE_LIMITS = {
    "minute": {"limit": 10, "window": 60},
    "hour": {"limit": 200, "window": 3600},
    "day": {"limit": 500, "window": 86400}
}

# Concurrent request tracking
class ConcurrentRequestTracker:
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.current_requests = 0
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            if self.current_requests >= self.max_concurrent:
                return False
            self.current_requests += 1
            return True

    async def release(self):
        async with self.lock:
            self.current_requests = max(0, self.current_requests - 1)

# Global concurrent request tracker
concurrent_tracker = ConcurrentRequestTracker(max_concurrent=5)

def generate_api_key() -> str:
    """Generate a secure API key"""
    # Generate 32 bytes (256 bits) of random data
    random_bytes = secrets.token_bytes(32)
    # Create a readable API key format: prefix_randomhex
    prefix = "kkm"
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}_{random_part}"

def hash_api_key(api_key: str) -> str:
    """Hash an API key for secure storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def create_api_key_for_user(user_id: int, key_name: Optional[str] = None) -> Dict[str, str]:
    """Create a new API key for a user"""
    try:
        conn = get_database()
        cursor = conn.cursor()

        # Generate new API key
        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)

        # Insert into database
        cursor.execute("""
            INSERT INTO api_keys (user_id, key_hash, name)
            VALUES (?, ?, ?)
        """, [user_id, key_hash, key_name or "Default API Key"])

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "api_key": api_key,
            "message": "API key created successfully. Store this key securely as it won't be shown again."
        }
    except Exception as e:
        raise Exception(f"Error creating API key: {str(e)}")

def validate_api_key(api_key: str) -> Optional[Dict]:
    """Validate an API key and return associated information"""
    try:
        conn = get_database()
        cursor = conn.cursor()

        key_hash = hash_api_key(api_key)

        # Get API key information
        cursor.execute("""
            SELECT ak.id, ak.user_id, ak.is_active, u.email, u.name
            FROM api_keys ak
            JOIN users u ON ak.user_id = u.id
            WHERE ak.key_hash = ? AND ak.is_active = 1
        """, [key_hash])

        result = cursor.fetchone()

        if not result:
            cursor.close()
            conn.close()
            return None

        api_key_id, user_id, is_active, email, name = result

        # Update last_used_at
        cursor.execute("""
            UPDATE api_keys
            SET last_used_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, [api_key_id])

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "api_key_id": api_key_id,
            "user_id": user_id,
            "email": email,
            "name": name
        }
    except Exception as e:
        raise Exception(f"Error validating API key: {str(e)}")

def check_rate_limit(api_key_id: int, endpoint: str) -> Tuple[bool, Dict[str, int]]:
    """Check if request is within rate limits using sliding window algorithm"""
    try:
        conn = get_database()
        cursor = conn.cursor()

        current_time = datetime.now()
        usage = {}

        for period, config in RATE_LIMITS.items():
            window_start = current_time - timedelta(seconds=config["window"])

            # Count requests in the sliding window
            cursor.execute("""
                SELECT COUNT(*) FROM rate_limit_logs
                WHERE api_key_id = ?
                AND timestamp > ?
                AND timestamp <= ?
            """, [api_key_id, window_start.isoformat(), current_time.isoformat()])

            count = cursor.fetchone()[0]
            usage[f"used_{period}"] = count
            usage[f"limit_{period}"] = config["limit"]

            if count >= config["limit"]:
                cursor.close()
                conn.close()
                return False, usage

        # Log this request
        cursor.execute("""
            INSERT INTO rate_limit_logs (api_key_id, endpoint, timestamp)
            VALUES (?, ?, ?)
        """, [api_key_id, endpoint, current_time.isoformat()])

        conn.commit()
        cursor.close()
        conn.close()

        # Increment usage counts
        for period in RATE_LIMITS:
            usage[f"used_{period}"] += 1

        return True, usage
    except Exception as e:
        raise Exception(f"Error checking rate limit: {str(e)}")

async def rate_limit_middleware(request: Request, api_key: Optional[str] = None):
    """Middleware for rate limiting and authentication"""
    # Check if API key is provided
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )

    # Validate API key
    api_key_info = validate_api_key(api_key)
    if not api_key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    # Check concurrent request limit
    if not await concurrent_tracker.acquire():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server overloaded. Maximum concurrent requests exceeded.",
            headers={"Retry-After": "5"}
        )

    try:
        # Check rate limits
        endpoint = str(request.url.path)
        within_limit, usage = check_rate_limit(api_key_info["api_key_id"], endpoint)

        if not within_limit:
            # Find which limit was exceeded
            exceeded_limits = []
            for period in ["minute", "hour", "day"]:
                if usage[f"used_{period}"] >= usage[f"limit_{period}"]:
                    exceeded_limits.append(f"{usage[f'limit_{period}']} requests per {period}")

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {', '.join(exceeded_limits)}",
                headers={
                    "X-RateLimit-Limit-Minute": str(usage["limit_minute"]),
                    "X-RateLimit-Limit-Hour": str(usage["limit_hour"]),
                    "X-RateLimit-Limit-Day": str(usage["limit_day"]),
                    "X-RateLimit-Used-Minute": str(usage["used_minute"]),
                    "X-RateLimit-Used-Hour": str(usage["used_hour"]),
                    "X-RateLimit-Used-Day": str(usage["used_day"]),
                    "Retry-After": "60"
                }
            )

        # Add rate limit headers to response
        request.state.rate_limit_headers = {
            "X-RateLimit-Limit-Minute": str(usage["limit_minute"]),
            "X-RateLimit-Limit-Hour": str(usage["limit_hour"]),
            "X-RateLimit-Limit-Day": str(usage["limit_day"]),
            "X-RateLimit-Remaining-Minute": str(usage["limit_minute"] - usage["used_minute"]),
            "X-RateLimit-Remaining-Hour": str(usage["limit_hour"] - usage["used_hour"]),
            "X-RateLimit-Remaining-Day": str(usage["limit_day"] - usage["used_day"])
        }

        # Store user info in request state for use in endpoints
        request.state.user = api_key_info

    finally:
        # Always release the concurrent request slot
        await concurrent_tracker.release()

def cleanup_old_logs(days_to_keep: int = 7):
    """Clean up old rate limit logs to prevent database bloat"""
    try:
        conn = get_database()
        cursor = conn.cursor()

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        cursor.execute("""
            DELETE FROM rate_limit_logs
            WHERE timestamp < ?
        """, [cutoff_date.isoformat()])

        deleted_count = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        return deleted_count
    except Exception as e:
        raise Exception(f"Error cleaning up logs: {str(e)}")

# Helper function to create a test user and API key
def create_test_user_and_key():
    """Create a test user and API key for development"""
    try:
        conn = get_database()
        cursor = conn.cursor()

        # Create test user
        test_email = "test@example.com"
        test_password_hash = hash_api_key("test_password")  # In production, use proper password hashing

        cursor.execute("""
            INSERT OR IGNORE INTO users (email, password_hash, name)
            VALUES (?, ?, ?)
        """, [test_email, test_password_hash, "Test User"])

        # Get user ID
        cursor.execute("SELECT id FROM users WHERE email = ?", [test_email])
        user_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        # Create API key for test user
        return create_api_key_for_user(user_id, "Test API Key")
    except Exception as e:
        raise Exception(f"Error creating test user: {str(e)}")
