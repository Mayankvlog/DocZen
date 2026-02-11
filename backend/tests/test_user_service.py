import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.database import init_db, get_database
from app.core.config import settings
from app.services.user_service import UserService
from app.schemas.user import UserCreate

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Setup test database"""
    # Use test database
    test_settings = settings
    test_settings.DATABASE_NAME = "test_doczen"
    test_settings.MONGODB_URL = "mongodb://localhost:27017"
    
    await init_db()
    db = await get_database()
    
    yield db
    
    # Cleanup
    await db.client.drop_database(test_settings.DATABASE_NAME)
    await db.client.close()

@pytest.fixture
def user_service(test_db):
    """Create user service instance"""
    return UserService(test_db)

@pytest.fixture
def sample_user():
    """Create sample user data"""
    return UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        full_name="Test User"
    )

@pytest.fixture
async def created_user(user_service, sample_user):
    """Create a user for testing"""
    user = await user_service.create_user(sample_user)
    yield user
    # Cleanup
    await user_service.collection.delete_one({"_id": user.id})

class TestUserService:
    """Test cases for UserService"""
    
    @pytest.mark.asyncio
    async def test_create_user(self, user_service, sample_user):
        """Test user creation"""
        user = await user_service.create_user(sample_user)
        
        assert user.email == sample_user.email
        assert user.full_name == sample_user.full_name
        assert user.is_email_verified == False
        assert user.id is not None
        
        # Cleanup
        await user_service.collection.delete_one({"_id": user.id})
    
    @pytest.mark.asyncio
    async def test_authenticate_user(self, user_service, created_user):
        """Test user authentication"""
        user = await user_service.authenticate_user(
            created_user.email, 
            "TestPassword123!"
        )
        
        assert user is not None
        assert user.id == created_user.id
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, user_service, created_user):
        """Test authentication with wrong password"""
        user = await user_service.authenticate_user(
            created_user.email, 
            "WrongPassword123!"
        )
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, user_service, created_user):
        """Test getting user by email"""
        user = await user_service.get_user_by_email(created_user.email)
        
        assert user is not None
        assert user.id == created_user.id
    
    @pytest.mark.asyncio
    async def test_update_user(self, user_service, created_user):
        """Test updating user"""
        from app.schemas.user import UserUpdate
        update_data = UserUpdate(full_name="Updated Name")
        
        updated_user = await user_service.update_user(created_user.id, update_data)
        
        assert updated_user.full_name == "Updated Name"
    
    @pytest.mark.asyncio
    async def test_change_password(self, user_service, created_user):
        """Test changing password"""
        success = await user_service.change_password(
            created_user.id,
            "TestPassword123!",
            "NewPassword123!"
        )
        
        assert success is True
