from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from models import UserRole, SessionMode, SessionStatus, TxType


# ── User ──────────────────────────────────────────────
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


# ── Expert ────────────────────────────────────────────
class ExpertApply(BaseModel):
    category: str = Field(max_length=50)
    title: str = Field(max_length=100)
    bio: Optional[str] = None
    hourly_rate: Decimal = Field(gt=0)
    rounds_rate: Optional[Decimal] = Field(default=None, gt=0)

class ExpertResp(BaseModel):
    id: int
    user_id: int
    category: str
    title: str
    bio: Optional[str]
    hourly_rate: Decimal
    rounds_rate: Optional[Decimal]
    is_verified: bool
    rating: Decimal

    class Config:
        from_attributes = True


# ── Chat Session ──────────────────────────────────────
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


# ── Message ───────────────────────────────────────────
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


# ── Wallet ────────────────────────────────────────────
class WalletRecharge(BaseModel):
    amount: Decimal = Field(gt=0)

class WalletResp(BaseModel):
    balance: Decimal
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Transaction ───────────────────────────────────────
class TransactionResp(BaseModel):
    id: int
    type: TxType
    amount: Decimal
    session_id: Optional[int]
    remark: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Auth ──────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
