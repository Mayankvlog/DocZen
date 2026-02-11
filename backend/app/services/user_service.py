from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserLogin, Token, TokenRefresh
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    generate_reset_token,
    verify_reset_token
)
from app.core.config import settings


class UserService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            user_data = await self.collection.find_one({"_id": user_id})
            if user_data:
                return User.from_dict(user_data)
        except Exception:
            pass
        return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_data = await self.collection.find_one({"email": email})
        if user_data:
            return User.from_dict(user_data)
        return None

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user_dict = user_data.model_dump()
        user_dict.pop("password")
        user_dict["hashed_password"] = hashed_password
        
        user = User(**user_dict)
        
        # Insert into database
        result = await self.collection.insert_one(user.to_dict())
        user.id = str(result.inserted_id)
        
        return user

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        await self.collection.update_one(
            {"_id": user.id},
            {"$set": {"last_login": datetime.utcnow(), "updated_at": datetime.utcnow()}}
        )
        
        return user

    async def create_tokens(self, user: User) -> Token:
        """Create access and refresh tokens for user"""
        access_token_data = {"sub": user.id, "email": user.email}
        refresh_token_data = {"sub": user.id, "email": user.email}
        
        access_token = create_access_token(access_token_data)
        refresh_token = create_refresh_token(refresh_token_data)
        
        # Store refresh token
        await self.collection.update_one(
            {"_id": user.id},
            {"$push": {"refresh_tokens": refresh_token}, "$set": {"updated_at": datetime.utcnow()}}
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    async def refresh_tokens(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token"""
        try:
            payload = verify_token(refresh_token, "refresh")
            user_id = payload.get("sub")
            
            user = await self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            # Check if refresh token is valid
            if refresh_token not in user.refresh_tokens:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            # Create new tokens
            return await self.create_tokens(user)
            
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

    async def update_user(self, user_id: str, user_update: UserUpdate) -> User:
        """Update user information"""
        update_data = user_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        await self.collection.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user

    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        if not verify_password(current_password, user.hashed_password):
            return False
        
        hashed_password = get_password_hash(new_password)
        
        await self.collection.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "hashed_password": hashed_password,
                    "updated_at": datetime.utcnow()
                },
                "$set": {"refresh_tokens": []}  # Invalidate all refresh tokens
            }
        )
        
        return True

    async def send_password_reset_email(self, email: str) -> None:
        """Send password reset email (mock implementation)"""
        user = await self.get_user_by_email(email)
        if not user:
            # Don't reveal if email exists or not
            return
        
        reset_token = generate_reset_token(email)
        reset_expires = datetime.utcnow() + timedelta(hours=1)
        
        await self.collection.update_one(
            {"_id": user.id},
            {
                "$set": {
                    "password_reset_token": reset_token,
                    "password_reset_expires": reset_expires,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # In a real implementation, send email here
        print(f"Password reset token for {email}: {reset_token}")

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password with token"""
        try:
            email = verify_reset_token(token)
            user = await self.get_user_by_email(email)
            
            if not user:
                return False
            
            if (user.password_reset_token != token or 
                user.password_reset_expires is None or 
                user.password_reset_expires < datetime.utcnow()):
                return False
            
            hashed_password = get_password_hash(new_password)
            
            await self.collection.update_one(
                {"_id": user.id},
                {
                    "$set": {
                        "hashed_password": hashed_password,
                        "password_reset_token": None,
                        "password_reset_expires": None,
                        "updated_at": datetime.utcnow()
                    },
                    "$set": {"refresh_tokens": []}  # Invalidate all refresh tokens
                }
            )
            
            return True
            
        except Exception:
            return False

    async def verify_email(self, token: str) -> bool:
        """Verify email with token"""
        try:
            payload = verify_token(token, "email_verification")
            user_id = payload.get("sub")
            
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            await self.collection.update_one(
                {"_id": user_id},
                {
                    "$set": {
                        "is_email_verified": True,
                        "email_verification_token": None,
                        "email_verification_expires": None,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return True
            
        except Exception:
            return False

    async def logout_user(self, user_id: str) -> None:
        """Logout user and invalidate tokens"""
        await self.collection.update_one(
            {"_id": user_id},
            {"$set": {"refresh_tokens": [], "updated_at": datetime.utcnow()}}
        )
