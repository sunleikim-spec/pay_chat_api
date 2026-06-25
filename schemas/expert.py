from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


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
