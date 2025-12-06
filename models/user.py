from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from enum import Enum

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler=None):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "cuenta@empresa.com",
                "password": "Demo1234"
            }
        }

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = Field(default=UserRole.USER)

class UserResponse(BaseModel):
    """Schema for user response"""
    id: str = Field(alias="_id")
    email: str
    role: str
    created_at: datetime
    
    @classmethod
    def from_mongo(cls, data: dict):
        """Convert MongoDB document to response model"""
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        use_enum_values = True

class UserInDB(BaseModel):
    """Schema for user in database"""
    id: str = Field(alias="_id")
    email: str
    password_hash: str
    role: str
    created_at: datetime
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class TokenResponse(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse