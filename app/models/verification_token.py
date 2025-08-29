from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
import secrets


class VerificationToken(Base):
    __tablename__ = "verification_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_type = Column(String, nullable=False)  # "email_verification" or "password_reset"
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="verification_tokens")
    
    @classmethod
    def generate_token(cls):
        return secrets.urlsafe_token(32)
    
    @classmethod
    def create_email_verification_token(cls, user_id: int):
        return cls(
            token=cls.generate_token(),
            user_id=user_id,
            token_type="email_verification",
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
    
    @classmethod
    def create_password_reset_token(cls, user_id: int):
        return cls(
            token=cls.generate_token(),
            user_id=user_id,
            token_type="password_reset",
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
    
    def is_valid(self) -> bool:
        return not self.used and self.expires_at > datetime.utcnow()