#!/usr/bin/env python3
"""
Production setup script for Render deployment
Run this after first deployment to setup initial data
"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.core.database import engine, Base
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def setup_database():
    """Setup database tables and initial data"""
    print("🔧 Setting up production database...")
    
    try:
        # Create all tables
        print("📊 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        
        # Check if admin user exists
        db = SessionLocal()
        admin_exists = db.query(User).filter(User.email == "admin@example.com").first()
        
        if not admin_exists:
            print("👤 Creating admin user...")
            admin_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("AdminPassword123!"),
                is_active=True,
                is_verified=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ Admin user created!")
            print("📧 Email: admin@example.com")
            print("🔐 Password: AdminPassword123!")
        else:
            print("✅ Admin user already exists!")
            
        db.close()
        
        # Test database connection
        print("🔍 Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connected: {version}")
            
        print("🎉 Production database setup complete!")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return False
    
    return True

async def setup_minio():
    """Setup MinIO bucket and initial configuration"""
    print("📁 Setting up MinIO storage...")
    
    try:
        from minio import Minio
        from app.core.config import settings
        
        # Initialize MinIO client  
        client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        
        # Create bucket if not exists
        bucket_name = settings.minio_bucket_name
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"✅ Created bucket: {bucket_name}")
        else:
            print(f"✅ Bucket already exists: {bucket_name}")
            
        # Create thumbnails bucket
        thumbnail_bucket = "thumbnails"  
        if not client.bucket_exists(thumbnail_bucket):
            client.make_bucket(thumbnail_bucket)
            print(f"✅ Created bucket: {thumbnail_bucket}")
        else:
            print(f"✅ Bucket already exists: {thumbnail_bucket}")
            
        print("🎉 MinIO storage setup complete!")
        
    except Exception as e:
        print(f"⚠️ MinIO setup error (will retry later): {e}")
        return False
        
    return True

async def main():
    """Main setup function"""
    print("🚀 Starting production setup...")
    print("=" * 50)
    
    # Setup database
    db_success = await setup_database()
    
    # Setup MinIO (optional, might fail if service not ready)
    minio_success = await setup_minio()
    
    print("=" * 50)
    if db_success:
        print("✅ Production setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test API endpoints")
        print("2. Configure email settings if needed")  
        print("3. Update CORS origins for your domain")
        print("4. Monitor logs in Render dashboard")
        
        if not minio_success:
            print("\n⚠️  MinIO setup failed - retry after MinIO service is ready")
            
    else:
        print("❌ Production setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())