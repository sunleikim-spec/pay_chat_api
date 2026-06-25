from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import hash_password, verify_password, create_access_token, get_current_user
import models, schemas

router = APIRouter(prefix="/api/users", tags=["用户"])


@router.post("/register", response_model=schemas.UserResp)
def register(body: schemas.UserRegister, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == body.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = models.User(
        username=body.username,
        phone=body.phone,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.flush()
    db.add(models.Wallet(user_id=user.id))
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
def login(body: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return {"access_token": create_access_token(user.id)}


@router.get("/me", response_model=schemas.UserResp)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user
