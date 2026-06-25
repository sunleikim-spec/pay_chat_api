from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import get_current_user
import models, schemas

router = APIRouter(prefix="/api/wallet", tags=["钱包"])


@router.get("", response_model=schemas.WalletResp)
def get_wallet(db: Session = Depends(get_db),
               current_user: models.User = Depends(get_current_user)):
    return current_user.wallet


@router.post("/recharge", response_model=schemas.WalletResp)
def recharge(body: schemas.WalletRecharge, db: Session = Depends(get_db),
             current_user: models.User = Depends(get_current_user)):
    wallet = current_user.wallet
    wallet.balance += body.amount
    db.add(models.Transaction(
        user_id=current_user.id,
        type=models.TxType.recharge,
        amount=body.amount,
        remark="手动充值",
    ))
    db.commit()
    db.refresh(wallet)
    return wallet


@router.get("/transactions", response_model=list[schemas.TransactionResp])
def get_transactions(db: Session = Depends(get_db),
                     current_user: models.User = Depends(get_current_user)):
    return db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).order_by(models.Transaction.created_at.desc()).limit(50).all()
