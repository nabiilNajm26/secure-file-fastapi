from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.api import auth, users, files
from app.core.database import engine, Base
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass


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

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")

@app.get("/")
def read_root():
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
def health_check():
    return {
        "status": "healthy",
        "service": "auth-file-api",
        "version": "1.0.0"
    }