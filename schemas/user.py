from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.user import UserRole


class UserRegister(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=6)
    phone: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResp(BaseModel):
    id: int
    username: str
    phone: Optional[str]
    role: UserRole
    avatar: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
