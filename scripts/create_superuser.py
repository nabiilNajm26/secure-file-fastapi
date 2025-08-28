#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from getpass import getpass
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User


def create_superuser():
    print("Creating superuser...")
    
    # Get user input
    email = input("Email: ")
    username = input("Username: ")
    password = getpass("Password: ")
    password_confirm = getpass("Confirm Password: ")
    
    if password != password_confirm:
        print("Passwords do not match!")
        return
    
    if len(password) < 8:
        print("Password must be at least 8 characters long!")
        return
    
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            if existing_user.email == email:
                print(f"User with email {email} already exists!")
            else:
                print(f"User with username {username} already exists!")
            return
        
        # Create superuser
        superuser = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_verified=True,
            is_superuser=True,
            full_name=input("Full name (optional): ") or None
        )
        
        db.add(superuser)
        db.commit()
        
        print(f"Superuser {username} created successfully!")
        
    except Exception as e:
        print(f"Error creating superuser: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_superuser()