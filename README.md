# Auth & File Upload API

A secure authentication system with file upload capabilities. Built to learn JWT authentication, file handling, and object storage with MinIO.

## What it does

This API handles user authentication (register, login, JWT tokens) and secure file uploads with image processing. Users can upload files to MinIO storage, and the system automatically processes images for different sizes.

## Tech Stack

- FastAPI (web framework)
- PostgreSQL (user data)
- Redis (caching, sessions)
- MinIO (S3-compatible file storage)
- JWT (authentication)
- Pillow (image processing)
- Docker (everything containerized)

## Features (planned)

- User registration with email verification
- JWT access & refresh tokens
- Password hashing and validation
- File upload with type/size validation
- Automatic image resizing and thumbnails
- Secure file serving with permissions
- File metadata tracking
- User profile management

## Quick start

**Prerequisites:**
- Docker and docker-compose
- Or: Python 3.11+, PostgreSQL, Redis, MinIO

**With Docker (recommended):**
```bash
git clone https://github.com/your-username/project-2-auth-file-api.git
cd project-2-auth-file-api
docker-compose up -d
```

**Services will be available at:**
- API: http://localhost:8001
- API Docs: http://localhost:8001/docs
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
- PostgreSQL: localhost:5433
- Redis: localhost:6379

**Manual setup:**
```bash
# Install dependencies
pip install -r requirements.txt

# Copy and edit environment file
cp .env.example .env
# Edit .env with your settings

# Run with uvicorn
uvicorn app.main:app --reload --port 8001
```

## Project structure

```
app/
├── main.py              # FastAPI app
├── api/                 # Route handlers
│   ├── auth.py          # Authentication routes
│   ├── users.py         # User management
│   └── files.py         # File upload/download
├── core/                # Core functionality
│   ├── config.py        # Settings
│   ├── database.py      # DB connection
│   ├── security.py      # JWT & password handling
│   └── storage.py       # MinIO client
├── models/              # Database models
│   ├── user.py          # User model
│   └── file.py          # File metadata model
├── schemas/             # Pydantic models
│   ├── auth.py          # Auth request/response
│   ├── user.py          # User schemas
│   └── file.py          # File schemas
├── services/            # Business logic
│   ├── auth_service.py  # Authentication logic
│   ├── user_service.py  # User operations
│   └── file_service.py  # File operations
└── utils/               # Utilities
    ├── email.py         # Email sending
    └── image.py         # Image processing
```

## Environment variables

Key settings (see .env.example for full list):

```env
# Database
DATABASE_URL=postgresql://postgres:postgres123@localhost:5433/auth_file_api

# JWT
JWT_SECRET_KEY=your-super-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# File uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,pdf,txt,doc,docx
```

## API endpoints (planned)

### Authentication
- POST `/auth/register` - Register new user
- POST `/auth/login` - Login user
- POST `/auth/refresh` - Refresh access token
- POST `/auth/logout` - Logout user
- POST `/auth/forgot-password` - Request password reset
- POST `/auth/reset-password` - Reset password

### Users
- GET `/users/me` - Get current user profile
- PUT `/users/me` - Update profile
- POST `/users/verify-email` - Verify email address

### Files
- POST `/files/upload` - Upload file(s)
- GET `/files/` - List user's files
- GET `/files/{file_id}` - Download file
- DELETE `/files/{file_id}` - Delete file
- GET `/files/{file_id}/info` - Get file metadata

## What I'm learning

- JWT authentication patterns (access + refresh tokens)
- File upload handling and validation
- Image processing with Pillow
- MinIO S3-compatible storage
- Redis for caching and sessions
- Email integration for verification
- More advanced FastAPI features

## Development plan

1. ✅ Basic project setup and structure
2. ⏳ Database models (User, File)
3. ⏳ Authentication system (JWT)
4. ⏳ File upload endpoints
5. ⏳ Image processing
6. ⏳ Email verification
7. ⏳ File permissions and sharing
8. ⏳ Testing and deployment

## Notes

This is a learning project to understand authentication patterns and file handling. The code structure is more complex than needed for a simple app, but it's designed to practice larger application architecture.

Currently just the basic setup - the actual auth and file features are coming soon!