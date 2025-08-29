from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from minio.error import S3Error
import logging
import traceback
from typing import Union

logger = logging.getLogger(__name__)


def add_error_handlers(app: FastAPI):
    """Add global error handlers to the FastAPI app"""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors"""
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(f"Validation error on {request.url.path}: {errors}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "details": errors,
                "path": request.url.path
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""
        logger.error(f"HTTP error on {request.url.path}: {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "status_code": exc.status_code,
                "path": request.url.path
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError):
        """Handle database errors"""
        logger.error(f"Database error on {request.url.path}: {str(exc)}")
        logger.error(traceback.format_exc())
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Database operation failed",
                "message": "An error occurred while processing your request",
                "path": request.url.path
            }
        )
    
    @app.exception_handler(S3Error)
    async def storage_exception_handler(request: Request, exc: S3Error):
        """Handle MinIO/S3 storage errors"""
        logger.error(f"Storage error on {request.url.path}: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Storage operation failed",
                "message": "An error occurred while handling file storage",
                "path": request.url.path
            }
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle value errors"""
        logger.error(f"Value error on {request.url.path}: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Bad Request",
                "message": str(exc),
                "path": request.url.path
            }
        )
    
    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError):
        """Handle permission errors"""
        logger.error(f"Permission error on {request.url.path}: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "Permission Denied",
                "message": "You don't have permission to perform this action",
                "path": request.url.path
            }
        )
    
    @app.exception_handler(FileNotFoundError)
    async def file_not_found_handler(request: Request, exc: FileNotFoundError):
        """Handle file not found errors"""
        logger.error(f"File not found on {request.url.path}: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "Not Found",
                "message": "The requested file was not found",
                "path": request.url.path
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other uncaught exceptions"""
        logger.error(f"Unhandled error on {request.url.path}: {str(exc)}")
        logger.error(traceback.format_exc())
        
        # In production, don't expose internal error details
        if hasattr(app.state, 'settings') and app.state.settings.environment == "production":
            message = "An internal server error occurred"
        else:
            message = str(exc)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": message,
                "path": request.url.path
            }
        )


class ErrorResponse:
    """Standardized error response"""
    
    @staticmethod
    def create(
        error: str,
        message: str,
        status_code: int,
        details: Union[dict, list, None] = None
    ) -> dict:
        response = {
            "error": error,
            "message": message,
            "status_code": status_code
        }
        if details:
            response["details"] = details
        return response
    
    @staticmethod
    def bad_request(message: str, details: Union[dict, list, None] = None) -> dict:
        return ErrorResponse.create(
            error="Bad Request",
            message=message,
            status_code=400,
            details=details
        )
    
    @staticmethod
    def unauthorized(message: str = "Authentication required") -> dict:
        return ErrorResponse.create(
            error="Unauthorized",
            message=message,
            status_code=401
        )
    
    @staticmethod
    def forbidden(message: str = "Access forbidden") -> dict:
        return ErrorResponse.create(
            error="Forbidden",
            message=message,
            status_code=403
        )
    
    @staticmethod
    def not_found(resource: str = "Resource") -> dict:
        return ErrorResponse.create(
            error="Not Found",
            message=f"{resource} not found",
            status_code=404
        )
    
    @staticmethod
    def conflict(message: str) -> dict:
        return ErrorResponse.create(
            error="Conflict",
            message=message,
            status_code=409
        )
    
    @staticmethod
    def internal_error(message: str = "Internal server error occurred") -> dict:
        return ErrorResponse.create(
            error="Internal Server Error",
            message=message,
            status_code=500
        )