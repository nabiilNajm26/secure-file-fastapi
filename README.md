# Auth & File Upload System

A complete authentication system with secure file handling. Built to understand JWT patterns and file storage, but evolved into something production-ready.

**🚀 Live Demo**: https://web-production-7b5e.up.railway.app  
**📚 Interactive API Docs**: https://web-production-7b5e.up.railway.app/docs

## What it does

- **Secure Authentication**: JWT-based auth with refresh tokens
- **Email Verification**: Account verification system  
- **File Upload**: Smart validation with image optimization
- **Rate Limiting**: Prevents abuse with Redis-based limiting
- **Production Ready**: Deployed on Railway with comprehensive error handling

## Quick Start

```bash
git clone https://github.com/your-username/project-2-auth-file-api.git
cd project-2-auth-file-api
docker-compose up -d
```

Visit http://localhost:8001/docs to explore the API.

## Features

✅ JWT authentication (access + refresh)  
✅ Email verification system  
✅ Secure file uploads with validation  
✅ Automatic image thumbnails  
✅ Rate limiting & error handling  
✅ Storage fallback system  
✅ Production deployment

## Documentation

- **[API Reference](docs/API.md)** - Complete endpoint documentation
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Docker, Railway, and manual setup
- **[Development Guide](docs/DEVELOPMENT.md)** - Architecture and development workflow

## Try it Live

**Quick test** (no setup needed):
1. Visit https://web-production-7b5e.up.railway.app/docs
2. Register → Login → Upload files
3. Use the "Authorize" button with your JWT token

```bash
# Quick curl test
curl -X POST "https://web-production-7b5e.up.railway.app/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"SecurePass123!","full_name":"Test User"}'
```

## Tech Stack

**Backend**: FastAPI + PostgreSQL + Redis + MinIO  
**Frontend**: Next.js 15 + TypeScript + Tailwind CSS *(planned)*  
**Deployment**: Railway + Docker  
**Security**: JWT + bcrypt + Rate limiting  

## What's Next: Frontend Development

🎯 **Goal**: Build a modern, responsive frontend to complete the full-stack application.

### Planned Frontend Stack
- **Next.js 15** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **React Query** for server state
- **Zustand** for client state
- **React Hook Form + Zod** for forms

### Development Phases

**Phase 1: Foundation**
- Setup Next.js project with TypeScript & Tailwind
- Create base layout and routing structure
- Build authentication forms (login/register)

**Phase 2: Integration**
- API client setup with Axios
- JWT token management and refresh
- Route protection middleware
- Connect auth forms to backend

**Phase 3: File Management**
- File upload component with drag & drop
- User dashboard for file management
- File list, preview, and actions
- Real-time upload progress

**Phase 4: Polish**
- Responsive design optimization
- Loading states and error handling
- Toast notifications and animations
- Dark mode support

### Key Features
✅ **Backend API Ready** - All endpoints implemented  
🔄 **Frontend Planning** - Detailed roadmap created  
⏳ **Next.js Setup** - Ready to begin development  
⏳ **Auth Interface** - Login/register forms  
⏳ **File Dashboard** - Upload and management UI  
⏳ **Production Deploy** - Frontend deployment to Vercel  

---