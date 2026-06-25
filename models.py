from sqlalchemy import Column, Integer, String, Text, Enum, DECIMAL, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class UserRole(str, enum.Enum):
    user = "user"
    expert = "expert"
    admin = "admin"


class SessionStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    ended = "ended"
    cancelled = "cancelled"


class SessionMode(str, enum.Enum):
    time = "time"        # 按时间
    rounds = "rounds"    # 按轮数


class TxType(str, enum.Enum):
    recharge = "recharge"
    payment = "payment"
    income = "income"
    refund = "refund"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True)
    password_hash = Column(String(128), nullable=False)
    avatar = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    expert_profile = relationship("ExpertProfile", back_populates="user", uselist=False)
    wallet = relationship("Wallet", back_populates="user", uselist=False)


class ExpertProfile(Base):
    __tablename__ = "expert_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    category = Column(String(50), nullable=False)
    title = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    hourly_rate = Column(DECIMAL(10, 2), nullable=False)
    rounds_rate = Column(DECIMAL(10, 2), nullable=True)  # 每轮收费
    is_verified = Column(Boolean, default=True)  # 第一版直接通过
    rating = Column(DECIMAL(3, 2), default=5.00)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="expert_profile")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    expert_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mode = Column(Enum(SessionMode), nullable=False)
    duration_minutes = Column(Integer, nullable=True)   # mode=time 时设定时长
    max_rounds = Column(Integer, nullable=True)          # mode=rounds 时设定轮数
    used_rounds = Column(Integer, default=0)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.pending)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    messages = relationship("Message", back_populates="session")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(DECIMAL(10, 2), default=0.00, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="wallet")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(TxType), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)
    remark = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
