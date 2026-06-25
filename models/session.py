from sqlalchemy import Column, Integer, Text, Enum, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class SessionStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    ended = "ended"
    cancelled = "cancelled"


class SessionMode(str, enum.Enum):
    time = "time"
    rounds = "rounds"


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    expert_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mode = Column(Enum(SessionMode), nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    max_rounds = Column(Integer, nullable=True)
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
