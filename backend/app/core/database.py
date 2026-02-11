from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
import os
from .config import settings

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def init_db():
    """Initialize database connection and create indexes"""
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        db.database = db.client[settings.DATABASE_NAME]
        
        # Create indexes for collections
        await create_indexes()
        
        print(f"Connected to MongoDB: {settings.DATABASE_NAME}")
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

async def create_indexes():
    """Create database indexes for performance"""
    try:
        # Users collection indexes
        try:
            await db.database.users.create_index("email", unique=True)
        except Exception:
            pass  # Index already exists
        
        try:
            await db.database.users.create_index("created_at")
        except Exception:
            pass
        
        # Files collection indexes
        try:
            await db.database.files.create_index("user_id")
        except Exception:
            pass
        
        try:
            await db.database.files.create_index("filename")
        except Exception:
            pass
        
        try:
            await db.database.files.create_index("created_at")
        except Exception:
            pass
        
        try:
            await db.database.files.create_index([("user_id", ASCENDING), ("created_at", -1)])
        except Exception:
            pass
        
        # Jobs collection indexes
        try:
            await db.database.jobs.create_index("job_id", unique=True)
        except Exception:
            pass
        
        try:
            await db.database.jobs.create_index("user_id")
        except Exception:
            pass
        
        try:
            await db.database.jobs.create_index("status")
        except Exception:
            pass
        
        try:
            await db.database.jobs.create_index("created_at")
        except Exception:
            pass
        
        # Sessions collection indexes with TTL
        try:
            await db.database.sessions.create_index("session_id", unique=True)
        except Exception:
            pass
        
        try:
            await db.database.sessions.create_index("user_id")
        except Exception:
            pass
        
        try:
            await db.database.sessions.create_index("expires_at", expireAfterSeconds=0)
        except Exception:
            pass
        
        # Shared links collection indexes with TTL
        try:
            await db.database.shared_links.create_index("link_id", unique=True)
        except Exception:
            pass
        
        try:
            await db.database.shared_links.create_index("file_id")
        except Exception:
            pass
        
        try:
            await db.database.shared_links.create_index("expires_at", expireAfterSeconds=0)
        except Exception:
            pass
        
        print("Database indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")
        raise

async def get_database():
    """Get database instance"""
    return db.database
