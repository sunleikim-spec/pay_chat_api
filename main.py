from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import engine, get_db
import models
from schemas import UserCreate, UserResp

# 程序启动自动创建数据表（不存在才创建，不会覆盖已有表）
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PayChatAPI", version="1.0")

@app.get("/")
def root():
    return {"message": "PayChatAPI running", "version": "1.1"}

# 创建用户
@app.post("/users", response_model=UserResp)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 根据ID查询用户
@app.get("/users/{uid}", response_model=UserResp)
def get_user(uid: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user