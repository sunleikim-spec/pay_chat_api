from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
from database import get_db
from utils.auth import get_current_user
import models, schemas

router = APIRouter(prefix="/api/sessions", tags=["聊天会话"])


def _calc_amount(expert: models.ExpertProfile, mode: models.SessionMode,
                 duration_minutes: int, max_rounds: int) -> Decimal:
    if mode == models.SessionMode.time:
        if not duration_minutes:
            raise HTTPException(status_code=400, detail="按时间模式需要填写 duration_minutes")
        return Decimal(expert.hourly_rate) * Decimal(duration_minutes) / 60
    else:
        if not max_rounds:
            raise HTTPException(status_code=400, detail="按轮数模式需要填写 max_rounds")
        if not expert.rounds_rate:
            raise HTTPException(status_code=400, detail="该专家未设置按轮收费")
        return Decimal(expert.rounds_rate) * max_rounds


@router.post("", response_model=schemas.SessionResp)
def create_session(body: schemas.SessionCreate, db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    expert_profile = db.query(models.ExpertProfile).filter(
        models.ExpertProfile.user_id == body.expert_id,
        models.ExpertProfile.is_verified == True,
    ).first()
    if not expert_profile:
        raise HTTPException(status_code=404, detail="专家不存在")
    if body.expert_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能向自己发起会话")

    amount = _calc_amount(expert_profile, body.mode, body.duration_minutes, body.max_rounds)

    wallet = current_user.wallet
    if not wallet or wallet.balance < amount:
        raise HTTPException(status_code=400, detail="余额不足，请先充值")

    wallet.balance -= amount
    db.add(models.Transaction(
        user_id=current_user.id,
        type=models.TxType.payment,
        amount=amount,
        remark=f"发起会话，专家ID {body.expert_id}",
    ))

    session = models.ChatSession(
        expert_id=body.expert_id,
        user_id=current_user.id,
        mode=body.mode,
        duration_minutes=body.duration_minutes,
        max_rounds=body.max_rounds,
        total_amount=amount,
        status=models.SessionStatus.active,
        start_time=datetime.utcnow(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=schemas.SessionResp)
def get_session(session_id: int, db: Session = Depends(get_db),
                current_user: models.User = Depends(get_current_user)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    if current_user.id not in (session.user_id, session.expert_id):
        raise HTTPException(status_code=403, detail="无权访问")
    return session


@router.post("/{session_id}/end", response_model=schemas.SessionResp)
def end_session(session_id: int, db: Session = Depends(get_db),
                current_user: models.User = Depends(get_current_user)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    if current_user.id not in (session.user_id, session.expert_id):
        raise HTTPException(status_code=403, detail="无权操作")
    if session.status != models.SessionStatus.active:
        raise HTTPException(status_code=400, detail="会话未在进行中")

    session.status = models.SessionStatus.ended
    session.end_time = datetime.utcnow()

    expert_wallet = db.query(models.Wallet).filter(
        models.Wallet.user_id == session.expert_id).first()
    if expert_wallet:
        expert_wallet.balance += session.total_amount
    db.add(models.Transaction(
        user_id=session.expert_id,
        type=models.TxType.income,
        amount=session.total_amount,
        session_id=session.id,
        remark="会话结束收入",
    ))
    db.commit()
    db.refresh(session)
    return session


@router.post("/{session_id}/messages", response_model=schemas.MessageResp)
def send_message(session_id: int, body: schemas.MessageSend,
                 db: Session = Depends(get_db),
                 current_user: models.User = Depends(get_current_user)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    if current_user.id not in (session.user_id, session.expert_id):
        raise HTTPException(status_code=403, detail="无权发送消息")
    if session.status != models.SessionStatus.active:
        raise HTTPException(status_code=400, detail="会话已结束")

    # 按轮计费：用户每发一条算一轮
    if session.mode == models.SessionMode.rounds and current_user.id == session.user_id:
        if session.used_rounds >= session.max_rounds:
            raise HTTPException(status_code=400, detail="已用完所有对话轮数")
        session.used_rounds += 1
        if session.used_rounds >= session.max_rounds:
            session.status = models.SessionStatus.ended
            session.end_time = datetime.utcnow()

    msg = models.Message(session_id=session_id, sender_id=current_user.id, content=body.content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


@router.get("/{session_id}/messages", response_model=list[schemas.MessageResp])
def get_messages(session_id: int, db: Session = Depends(get_db),
                 current_user: models.User = Depends(get_current_user)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    if current_user.id not in (session.user_id, session.expert_id):
        raise HTTPException(status_code=403, detail="无权访问")
    return db.query(models.Message).filter(
        models.Message.session_id == session_id
    ).order_by(models.Message.created_at).all()
