from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, Response
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request.
    Checks for X-Forwarded-For header for proxy scenarios.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "127.0.0.1"
    return ip


# Create limiter instance
limiter = Limiter(
    key_func=get_client_ip,
    default_limits=["200 per minute", "1000 per hour"],
    storage_uri=settings.redis_url if hasattr(settings, 'redis_url') else None,
    enabled=True
)


# Rate limit configurations for different endpoints
RATE_LIMITS = {
    "auth": {
        "register": "5 per minute",
        "login": "10 per minute",
        "forgot_password": "3 per minute",
        "verify_email": "10 per minute",
        "resend_verification": "3 per minute",
        "reset_password": "5 per minute"
    },
    "files": {
        "upload": "20 per minute",
        "download": "50 per minute",
        "list": "100 per minute",
        "delete": "20 per minute"
    },
    "users": {
        "profile": "30 per minute",
        "update": "10 per minute",
        "list": "50 per minute"
    }
}


def add_rate_limiting(app):
    """
    Add rate limiting middleware to FastAPI app
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    logger.info("Rate limiting middleware added")


def get_rate_limit(endpoint_type: str, operation: str) -> str:
    """
    Get rate limit for specific endpoint
    
    Args:
        endpoint_type: Type of endpoint (auth, files, users)
        operation: Specific operation (login, upload, etc.)
    
    Returns:
        Rate limit string
    """
    return RATE_LIMITS.get(endpoint_type, {}).get(operation, "100 per minute")


class RateLimitDecorators:
    """
    Pre-configured rate limit decorators for common operations
    """
    
    @staticmethod
    def auth_register():
        return limiter.limit("5 per minute")
    
    @staticmethod
    def auth_login():
        return limiter.limit("10 per minute")
    
    @staticmethod
    def auth_password_reset():
        return limiter.limit("3 per minute")
    
    @staticmethod
    def file_upload():
        return limiter.limit("20 per minute")
    
    @staticmethod
    def file_download():
        return limiter.limit("50 per minute")
    
    @staticmethod
    def user_update():
        return limiter.limit("10 per minute")
    
    @staticmethod
    def api_general():
        return limiter.limit("100 per minute")