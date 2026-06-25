from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class ExpertProfile(Base):
    __tablename__ = "expert_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    category = Column(String(50), nullable=False)
    title = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    hourly_rate = Column(DECIMAL(10, 2), nullable=False)
    rounds_rate = Column(DECIMAL(10, 2), nullable=True)
    is_verified = Column(Boolean, default=True)
    rating = Column(DECIMAL(3, 2), default=5.00)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="expert_profile")
