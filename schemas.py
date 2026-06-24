from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None

class UserResp(UserCreate):
    id: int

    class Config:
        orm_mode = True