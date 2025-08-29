from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.api import auth, users, files
from app.core.database import engine, Base
from app.core.config import settings
from app.core.rate_limit import add_rate_limiting, limiter
from app.core.error_handlers import add_error_handlers
from app.core.logging_config import setup_logging
import logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger = setup_logging()
    logger.info("Starting Auth & File Upload API")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    yield
    # Shutdown
    logger.info("Shutting down Auth & File Upload API")


app = FastAPI(
    title="Auth & File Upload API",
    description="Authentication system with secure file upload capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS based on environment
allowed_origins = ["*"] if settings.environment == "development" else [
    "https://your-frontend-domain.com",
    "https://www.your-frontend-domain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Add rate limiting
add_rate_limiting(app)

# Add error handlers
add_error_handlers(app)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")

@app.get("/")
@limiter.limit("60 per minute")
def read_root(request: Request):
    return {
        "message": "Auth & File Upload API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "files": "/api/v1/files",
            "health": "/health"
        }
    }

@app.get("/health")
@limiter.limit("60 per minute")
def health_check(request: Request):
    return {
        "status": "healthy",
        "service": "auth-file-api",
        "version": "1.0.0"
    }