from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from models.session import SessionMode, SessionStatus


class SessionCreate(BaseModel):
    expert_id: int
    mode: SessionMode
    duration_minutes: Optional[int] = Field(default=None, gt=0)
    max_rounds: Optional[int] = Field(default=None, gt=0)

class SessionResp(BaseModel):
    id: int
    expert_id: int
    user_id: int
    mode: SessionMode
    duration_minutes: Optional[int]
    max_rounds: Optional[int]
    used_rounds: int
    total_amount: Decimal
    status: SessionStatus
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class MessageSend(BaseModel):
    content: str = Field(min_length=1)

class MessageResp(BaseModel):
    id: int
    session_id: int
    sender_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
