import logging
import logging.config
import sys
from pathlib import Path
from app.core.config import settings


def setup_logging():
    """Configure logging for the application"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Determine log level based on environment
    log_level = "DEBUG" if settings.debug else "INFO"
    
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "default",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/errors.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "app": {
                "level": log_level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": "WARNING" if settings.environment == "production" else "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console", "file"]
        }
    }
    
    # Apply logging configuration
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for {settings.environment} environment")
    logger.info(f"Log level set to {log_level}")
    
    return logger


class RequestLogger:
    """Middleware for logging HTTP requests"""
    
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger("app.requests")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope["path"]
            method = scope["method"]
            
            # Log request
            self.logger.info(f"Request: {method} {path}")
            
            # Process request
            await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)