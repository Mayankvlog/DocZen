import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.services.user_service import UserService
from app.schemas.user import UserCreate

@pytest.mark.asyncio
async def test_user_service_basic():
    """Basic test for UserService without fixtures"""
    # Create test database connection
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_doczen"]
    
    # Create service
    user_service = UserService(db)
    
    # Test data
    user_data = UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        full_name="Test User"
    )
    
    try:
        # Test user creation
        user = await user_service.create_user(user_data)
        assert user.email == user_data.email
        assert user.full_name == user_data.full_name
        assert user.id is not None
        
        # Test authentication
        auth_user = await user_service.authenticate_user(
            user_data.email,
            "TestPassword123!"
        )
        assert auth_user is not None
        assert auth_user.id == user.id
        
        # Test wrong password
        wrong_auth = await user_service.authenticate_user(
            user_data.email,
            "WrongPassword123!"
        )
        assert wrong_auth is None
        
        # Test get user by email
        found_user = await user_service.get_user_by_email(user_data.email)
        assert found_user is not None
        assert found_user.id == user.id
        
        print("✅ All user service tests passed!")
        
    finally:
        # Cleanup
        await db.users.delete_many({"email": user_data.email})
        await client.close()

@pytest.mark.asyncio
async def test_user_password_change():
    """Test password change functionality"""
    # Create test database connection
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_doczen"]
    
    # Create service
    user_service = UserService(db)
    
    # Test data
    user_data = UserCreate(
        email="test2@example.com",
        password="TestPassword123!",
        full_name="Test User 2"
    )
    
    try:
        # Create user
        user = await user_service.create_user(user_data)
        
        # Test password change
        success = await user_service.change_password(
            user.id,
            "TestPassword123!",
            "NewPassword123!"
        )
        assert success is True
        
        # Test authentication with new password
        auth_user = await user_service.authenticate_user(
            user_data.email,
            "NewPassword123!"
        )
        assert auth_user is not None
        
        # Test authentication with old password fails
        old_auth = await user_service.authenticate_user(
            user_data.email,
            "TestPassword123!"
        )
        assert old_auth is None
        
        print("✅ Password change test passed!")
        
    finally:
        # Cleanup
        await db.users.delete_many({"email": user_data.email})
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_user_service_basic())
    asyncio.run(test_user_password_change())
