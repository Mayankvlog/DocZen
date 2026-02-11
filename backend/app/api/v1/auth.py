from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from app.core.database import get_database
from app.core.security import verify_token
from app.schemas.user import UserResponse, UserCreate, UserUpdate, UserLogin, Token, TokenRefresh, PasswordReset, PasswordResetConfirm, PasswordChange, EmailVerification
from app.services.user_service import UserService
from app.models.user import User

router = APIRouter()
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_database)
) -> User:
    """Get current authenticated user"""
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db = Depends(get_database)):
    """Register a new user"""
    user_service = UserService(db)
    
    # Check if user already exists
    existing_user = await user_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    user = await user_service.create_user(user_data)
    return user

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db = Depends(get_database)):
    """Authenticate user and return tokens"""
    user_service = UserService(db)
    
    user = await user_service.authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    tokens = await user_service.create_tokens(user)
    return tokens

@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, db = Depends(get_database)):
    """Refresh access token"""
    user_service = UserService(db)
    
    tokens = await user_service.refresh_tokens(token_data.refresh_token)
    return tokens

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update current user information"""
    user_service = UserService(db)
    user = await user_service.update_user(current_user.id, user_update)
    return user

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Change user password"""
    user_service = UserService(db)
    
    success = await user_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    
    return {"message": "Password changed successfully"}

@router.post("/forgot-password")
async def forgot_password(
    reset_data: PasswordReset,
    db = Depends(get_database)
):
    """Send password reset email"""
    user_service = UserService(db)
    
    await user_service.send_password_reset_email(reset_data.email)
    
    return {"message": "Password reset email sent"}

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db = Depends(get_database)
):
    """Reset password with token"""
    user_service = UserService(db)
    
    success = await user_service.reset_password(reset_data.token, reset_data.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    
    return {"message": "Password reset successfully"}

@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerification,
    db = Depends(get_database)
):
    """Verify email address"""
    user_service = UserService(db)
    
    success = await user_service.verify_email(verification_data.token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )
    
    return {"message": "Email verified successfully"}

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user), db = Depends(get_database)):
    """Logout user and invalidate tokens"""
    user_service = UserService(db)
    
    await user_service.logout_user(current_user.id)
    
    return {"message": "Logged out successfully"}
