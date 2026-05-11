from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    name:     str = Field(..., min_length=2, max_length=120)
    email:    EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    name:      Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id:         str
    name:       str
    email:      str
    is_active:  bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class LoginResponse(BaseModel):
    message:      str
    access_token: str
    token_type:   str
    user:         UserResponse
