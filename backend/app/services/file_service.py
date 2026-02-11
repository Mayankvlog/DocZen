import os
import uuid
import hashlib
import mimetypes
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status, UploadFile
from app.models.file import File, ShareLink
from app.schemas.file import FileCreate, FileUpdate, ShareLinkCreate
from app.core.config import settings
from app.models.user import User


class FileService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.files
        self.shared_links_collection = db.shared_links

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID (needed for authentication)"""
        user_data = await self.db.users.find_one({"_id": user_id})
        if user_data:
            return User.from_dict(user_data)
        return None

    def is_allowed_file(self, filename: str) -> bool:
        """Check if file type is allowed"""
        if not filename:
            return False
        
        file_ext = os.path.splitext(filename)[1].lower().lstrip('.')
        return file_ext in settings.ALLOWED_EXTENSIONS

    async def upload_file(self, file: UploadFile, user_id: str) -> File:
        """Upload a file"""
        if not self.is_allowed_file(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File type not allowed"
            )

        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{file_id}{file_ext}"
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(settings.UPLOAD_DIR, user_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Get file info
            file_size = len(content)
            mime_type = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
            file_type = os.path.splitext(file.filename)[1].lower().lstrip('.')
            
            # Create file record
            file_data = {
                "_id": file_id,
                "filename": filename,
                "original_filename": file.filename,
                "file_type": file_type,
                "file_size": file_size,
                "mime_type": mime_type,
                "file_path": file_path,
                "user_id": user_id,
                "is_favorite": False,
                "tags": [],
                "metadata": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "download_count": 0,
                "is_public": False
            }
            
            await self.collection.insert_one(file_data)
            
            return File.from_dict(file_data)
            
        except Exception as e:
            # Clean up file if database insert fails
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )

    async def get_user_files(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        file_type: Optional[str] = None,
        is_favorite: Optional[bool] = None
    ) -> List[File]:
        """Get user's files with filters"""
        query = {"user_id": user_id}
        
        if search:
            query["original_filename"] = {"$regex": search, "$options": "i"}
        
        if file_type:
            query["file_type"] = file_type
        
        if is_favorite is not None:
            query["is_favorite"] = is_favorite
        
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        files_data = await cursor.to_list(length=limit)
        
        return [File.from_dict(file_data) for file_data in files_data]

    async def get_file(self, file_id: str, user_id: str) -> Optional[File]:
        """Get file by ID and user"""
        file_data = await self.collection.find_one({"_id": file_id, "user_id": user_id})
        if file_data:
            return File.from_dict(file_data)
        return None

    async def update_file(self, file_id: str, user_id: str, file_update: dict) -> Optional[File]:
        """Update file metadata"""
        update_data = {k: v for k, v in file_update.items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": file_id, "user_id": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count:
            return await self.get_file(file_id, user_id)
        return None

    async def delete_file(self, file_id: str, user_id: str) -> bool:
        """Delete a file"""
        file = await self.get_file(file_id, user_id)
        if not file:
            return False
        
        # Delete physical file
        try:
            if os.path.exists(file.file_path):
                os.remove(file.file_path)
        except Exception:
            pass  # Continue even if file deletion fails
        
        # Delete from database
        result = await self.collection.delete_one({"_id": file_id, "user_id": user_id})
        
        return result.deleted_count > 0

    async def create_share_link(self, share_data: ShareLinkCreate) -> ShareLink:
        """Create a share link for a file"""
        link_id = str(uuid.uuid4())
        
        share_link_data = {
            "_id": str(uuid.uuid4()),
            "link_id": link_id,
            "file_id": share_data.file_id,
            "user_id": share_data.user_id,
            "expires_at": share_data.expires_at,
            "download_limit": share_data.download_limit,
            "password": share_data.password,
            "download_count": 0,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        await self.shared_links_collection.insert_one(share_link_data)
        
        return ShareLink.from_dict(share_link_data)

    async def get_shared_file(self, link_id: str, password: Optional[str] = None) -> Optional[File]:
        """Get shared file via link"""
        share_link_data = await self.shared_links_collection.find_one({"link_id": link_id, "is_active": True})
        if not share_link_data:
            return None
        
        share_link = ShareLink.from_dict(share_link_data)
        
        # Check if link has expired
        if share_link.expires_at and share_link.expires_at < datetime.utcnow():
            return None
        
        # Check download limit
        if share_link.download_limit and share_link.download_count >= share_link.download_limit:
            return None
        
        # Check password
        if share_link.password and share_link.password != password:
            return None
        
        # Get file
        file_data = await self.collection.find_one({"_id": share_link.file_id})
        if not file_data:
            return None
        
        # Increment download count
        await self.shared_links_collection.update_one(
            {"link_id": link_id},
            {"$inc": {"download_count": 1}}
        )
        
        return File.from_dict(file_data)
