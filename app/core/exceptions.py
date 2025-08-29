from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class APIException(HTTPException):
    """Base API Exception"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class AuthenticationException(APIException):
    """Authentication related exceptions"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationException(APIException):
    """Authorization related exceptions"""
    def __init__(self, detail: str = "Not authorized to perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class NotFoundException(APIException):
    """Resource not found exception"""
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found"
        )


class ValidationException(APIException):
    """Validation exception"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class ConflictException(APIException):
    """Conflict exception for duplicate resources"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class FileSizeException(APIException):
    """File size exceeds limit"""
    def __init__(self, max_size: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {max_size} bytes"
        )


class FileTypeException(APIException):
    """Invalid file type"""
    def __init__(self, allowed_types: list):
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
        )


class StorageException(APIException):
    """Storage related exceptions"""
    def __init__(self, detail: str = "Storage operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class DatabaseException(APIException):
    """Database operation exceptions"""
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class EmailException(APIException):
    """Email sending exceptions"""
    def __init__(self, detail: str = "Failed to send email"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class TokenException(APIException):
    """Token related exceptions"""
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class RateLimitException(APIException):
    """Rate limit exceeded"""
    def __init__(self, retry_after: Optional[int] = None):
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers=headers
        )


class ServiceUnavailableException(APIException):
    """Service temporarily unavailable"""
    def __init__(self, detail: str = "Service temporarily unavailable"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )