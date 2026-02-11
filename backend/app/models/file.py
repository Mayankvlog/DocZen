from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from app.schemas.file import FileType


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class File(MongoBaseModel):
    filename: str
    original_filename: str
    file_type: FileType
    file_size: int
    mime_type: str
    file_path: str
    user_id: str
    is_favorite: bool = False
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    thumbnail_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    download_count: int = 0
    is_public: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "file_path": self.file_path,
            "user_id": self.user_id,
            "is_favorite": self.is_favorite,
            "tags": self.tags,
            "metadata": self.metadata,
            "thumbnail_path": self.thumbnail_path,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "download_count": self.download_count,
            "is_public": self.is_public,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "File":
        if "_id" in data:
            data["id"] = data.pop("_id")
        return cls(**data)


class ShareLink(MongoBaseModel):
    link_id: str
    file_id: str
    user_id: str
    expires_at: Optional[datetime] = None
    download_limit: Optional[int] = None
    password: Optional[str] = None
    download_count: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "link_id": self.link_id,
            "file_id": self.file_id,
            "user_id": self.user_id,
            "expires_at": self.expires_at,
            "download_limit": self.download_limit,
            "password": self.password,
            "download_count": self.download_count,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShareLink":
        if "_id" in data:
            data["id"] = data.pop("_id")
        return cls(**data)
