from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from models.wallet import TxType


class WalletRecharge(BaseModel):
    amount: Decimal = Field(gt=0)

class WalletResp(BaseModel):
    balance: Decimal
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class TransactionResp(BaseModel):
    id: int
    type: TxType
    amount: Decimal
    session_id: Optional[int]
    remark: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
