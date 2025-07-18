from functools import wraps
from typing import Optional
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import APIKeyHeader
from .auth import rate_limit_middleware, API_KEY_HEADER

# Dependency for rate limiting
async def require_api_key(
    request: Request,
    response: Response,
    api_key: Optional[str] = Depends(API_KEY_HEADER)
):
    """
    FastAPI dependency for API key authentication and rate limiting.

    Usage:
        @app.get("/protected")
        async def protected_endpoint(auth=Depends(require_api_key)):
            return {"message": "Protected content"}
    """
    # Call the rate limit middleware
    await rate_limit_middleware(request, api_key)

    # Add rate limit headers to response
    if hasattr(request.state, 'rate_limit_headers'):
        for header, value in request.state.rate_limit_headers.items():
            response.headers[header] = value

    # Return user information for use in endpoint
    return request.state.user if hasattr(request.state, 'user') else None

# Optional: Decorator for rate limiting (alternative approach)
def rate_limited(func):
    """
    Decorator for rate limiting endpoints.

    Usage:
        @app.get("/protected")
        @rate_limited
        async def protected_endpoint(request: Request, api_key: str = Depends(API_KEY_HEADER)):
            return {"message": "Protected content"}
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract request and api_key from kwargs
        request = None
        api_key = None

        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break

        if not request:
            request = kwargs.get('request')

        api_key = kwargs.get('api_key')

        if not request or not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Rate limiting configuration error"
            )

        # Apply rate limiting
        await rate_limit_middleware(request, api_key)

        # Call the original function
        return await func(*args, **kwargs)

    return wrapper

# Middleware for adding rate limit headers to all responses
async def add_rate_limit_headers(request: Request, call_next):
    """
    Middleware to add rate limit headers to responses.
    Should be added to FastAPI app:

    app.add_middleware(add_rate_limit_headers)
    """
    response = await call_next(request)

    # Add rate limit headers if they exist in request state
    if hasattr(request.state, 'rate_limit_headers'):
        for header, value in request.state.rate_limit_headers.items():
            response.headers[header] = value

    return response

# Helper function to get current rate limit status
async def get_rate_limit_status(api_key: str) -> dict:
    """
    Get current rate limit status for an API key.

    Returns:
        dict: Current usage and limits for all time windows
    """
    from .auth import validate_api_key, check_rate_limit

    # Validate API key
    api_key_info = validate_api_key(api_key)
    if not api_key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    # Check rate limits without logging
    try:
        # We'll check the rate limit without actually logging a request
        # This is a read-only operation
        from .database import get_database
        from datetime import datetime, timedelta
        from .auth import RATE_LIMITS

        conn = get_database()
        cursor = conn.cursor()

        current_time = datetime.now()
        usage = {}

        for period, config in RATE_LIMITS.items():
            window_start = current_time - timedelta(seconds=config["window"])

            cursor.execute("""
                SELECT COUNT(*) FROM rate_limit_logs
                WHERE api_key_id = ?
                AND timestamp > ?
                AND timestamp <= ?
            """, [api_key_info["api_key_id"], window_start.isoformat(), current_time.isoformat()])

            count = cursor.fetchone()[0]
            usage[f"used_{period}"] = count
            usage[f"limit_{period}"] = config["limit"]
            usage[f"remaining_{period}"] = max(0, config["limit"] - count)

        cursor.close()
        conn.close()

        return {
            "status": "active",
            "user": {
                "email": api_key_info["email"],
                "name": api_key_info["name"]
            },
            "limits": {
                "per_minute": {
                    "limit": usage["limit_minute"],
                    "used": usage["used_minute"],
                    "remaining": usage["remaining_minute"]
                },
                "per_hour": {
                    "limit": usage["limit_hour"],
                    "used": usage["used_hour"],
                    "remaining": usage["remaining_hour"]
                },
                "per_day": {
                    "limit": usage["limit_day"],
                    "used": usage["used_day"],
                    "remaining": usage["remaining_day"]
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking rate limit status: {str(e)}"
        )
