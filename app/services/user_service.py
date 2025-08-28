from typing import Optional, List
from sqlalchemy.orm import Session
from app.core import security
from app.models.user import User
from app.schemas.user import UserUpdate


class UserService:
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user: User, user_update: UserUpdate) -> User:
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Handle password update separately
        if "password" in update_data:
            hashed_password = security.get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        # Check for unique constraints
        if "email" in update_data and update_data["email"] != user.email:
            existing_user = UserService.get_user_by_email(db, update_data["email"])
            if existing_user:
                raise ValueError("Email already registered")
        
        if "username" in update_data and update_data["username"] != user.username:
            existing_user = UserService.get_user_by_username(db, update_data["username"])
            if existing_user:
                raise ValueError("Username already taken")
        
        # Update user
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        user = UserService.get_user(db, user_id)
        if user:
            db.delete(user)
            db.commit()
            return True
        return False
    
    @staticmethod
    def verify_user_email(db: Session, user: User) -> User:
        user.is_verified = True
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def change_password(db: Session, user: User, current_password: str, new_password: str) -> bool:
        if not security.verify_password(current_password, user.hashed_password):
            return False
        
        user.hashed_password = security.get_password_hash(new_password)
        db.add(user)
        db.commit()
        return True