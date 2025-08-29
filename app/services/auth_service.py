from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core import security
from app.core.email import email_service
from app.models.user import User
from app.models.verification_token import VerificationToken
from app.schemas.auth import Token, RegisterRequest
from app.schemas.user import UserCreate
import logging

logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not security.verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def create_user(db: Session, user_data: RegisterRequest) -> User:
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            if existing_user.email == user_data.email:
                raise ValueError("Email already registered")
            if existing_user.username == user_data.username:
                raise ValueError("Username already taken")
        
        # Create new user
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=security.get_password_hash(user_data.password),
            full_name=user_data.full_name,
            is_active=True,
            is_verified=False,
            is_superuser=False
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create and send verification email
        verification_token = VerificationToken.create_email_verification_token(db_user.id)
        db.add(verification_token)
        db.commit()
        
        try:
            email_service.send_verification_email(db_user.email, verification_token.token)
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
        
        return db_user
    
    @staticmethod
    def create_tokens(user_id: int) -> Token:
        access_token = security.create_access_token(subject=user_id)
        refresh_token = security.create_refresh_token(subject=user_id)
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    @staticmethod
    def verify_refresh_token(db: Session, refresh_token: str) -> Optional[User]:
        payload = security.decode_token(refresh_token)
        if not payload:
            return None
        
        # Check if it's a refresh token
        if payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        return user if user and user.is_active else None
    
    @staticmethod
    def verify_email(db: Session, token: str) -> bool:
        verification_token = db.query(VerificationToken).filter(
            VerificationToken.token == token,
            VerificationToken.token_type == "email_verification"
        ).first()
        
        if not verification_token or not verification_token.is_valid():
            return False
        
        user = verification_token.user
        user.is_verified = True
        verification_token.used = True
        
        db.commit()
        return True
    
    @staticmethod
    def request_password_reset(db: Session, email: str) -> bool:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False
        
        # Create password reset token
        reset_token = VerificationToken.create_password_reset_token(user.id)
        db.add(reset_token)
        db.commit()
        
        try:
            email_service.send_password_reset_email(user.email, reset_token.token)
            return True
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            return False
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        verification_token = db.query(VerificationToken).filter(
            VerificationToken.token == token,
            VerificationToken.token_type == "password_reset"
        ).first()
        
        if not verification_token or not verification_token.is_valid():
            return False
        
        user = verification_token.user
        user.hashed_password = security.get_password_hash(new_password)
        verification_token.used = True
        
        db.commit()
        return True
    
    @staticmethod
    def resend_verification_email(db: Session, email: str) -> bool:
        user = db.query(User).filter(User.email == email).first()
        if not user or user.is_verified:
            return False
        
        # Invalidate previous tokens
        db.query(VerificationToken).filter(
            VerificationToken.user_id == user.id,
            VerificationToken.token_type == "email_verification",
            VerificationToken.used == False
        ).update({"used": True})
        
        # Create new token
        verification_token = VerificationToken.create_email_verification_token(user.id)
        db.add(verification_token)
        db.commit()
        
        try:
            email_service.send_verification_email(user.email, verification_token.token)
            return True
        except Exception as e:
            logger.error(f"Failed to resend verification email: {str(e)}")
            return False