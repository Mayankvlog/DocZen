from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from app.schemas.user import UserRole, UserStatus


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


class User(MongoBaseModel):
    email: str
    full_name: Optional[str] = None
    hashed_password: str
    role: UserRole = UserRole.FREE
    status: UserStatus = UserStatus.ACTIVE
    is_email_verified: bool = False
    is_mfa_enabled: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    storage_used: int = 0
    storage_quota: int = 1073741824  # 1GB in bytes
    refresh_tokens: List[str] = []
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None
    email_verification_token: Optional[str] = None
    email_verification_expires: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "hashed_password": self.hashed_password,
            "role": self.role,
            "status": self.status,
            "is_email_verified": self.is_email_verified,
            "is_mfa_enabled": self.is_mfa_enabled,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_login": self.last_login,
            "storage_used": self.storage_used,
            "storage_quota": self.storage_quota,
            "refresh_tokens": self.refresh_tokens,
            "password_reset_token": self.password_reset_token,
            "password_reset_expires": self.password_reset_expires,
            "email_verification_token": self.email_verification_token,
            "email_verification_expires": self.email_verification_expires,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        if "_id" in data:
            data["id"] = data.pop("_id")
        return cls(**data)
