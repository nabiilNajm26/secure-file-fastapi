from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.core.deps import get_db
from app.core.rate_limit import limiter
from app.schemas.auth import Token, RegisterRequest, RefreshTokenRequest
from app.schemas.user import User
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


class EmailRequest(BaseModel):
    email: EmailStr


class PasswordResetRequest(BaseModel):
    token: str
    new_password: str


@router.post("/register", response_model=User)
@limiter.limit("5 per minute")
def register(
    request: Request,
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    try:
        user = AuthService.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
@limiter.limit("10 per minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return AuthService.create_tokens(user.id)


@router.post("/refresh", response_model=Token)
@limiter.limit("20 per minute")
def refresh_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    user = AuthService.verify_refresh_token(db, refresh_data.refresh_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return AuthService.create_tokens(user.id)


@router.post("/verify-email")
@limiter.limit("10 per minute")
def verify_email(
    request: Request,
    token: str,
    db: Session = Depends(get_db)
):
    if AuthService.verify_email(db, token):
        return {"message": "Email verified successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )


@router.post("/resend-verification")
@limiter.limit("3 per minute")
def resend_verification(
    request: Request,
    email_request: EmailRequest,
    db: Session = Depends(get_db)
):
    if AuthService.resend_verification_email(db, email_request.email):
        return {"message": "Verification email sent"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to send verification email"
        )


@router.post("/forgot-password")
@limiter.limit("3 per minute")
def forgot_password(
    request: Request,
    email_request: EmailRequest,
    db: Session = Depends(get_db)
):
    AuthService.request_password_reset(db, email_request.email)
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
@limiter.limit("5 per minute")
def reset_password(
    request: Request,
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    if AuthService.reset_password(db, reset_request.token, reset_request.new_password):
        return {"message": "Password reset successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )