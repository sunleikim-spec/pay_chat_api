from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import get_current_user
import models, schemas

router = APIRouter(prefix="/api/experts", tags=["专家"])


@router.post("/apply", response_model=schemas.ExpertResp)
def apply(body: schemas.ExpertApply, db: Session = Depends(get_db),
          current_user: models.User = Depends(get_current_user)):
    if current_user.expert_profile:
        raise HTTPException(status_code=400, detail="已提交过专家申请")
    profile = models.ExpertProfile(
        user_id=current_user.id,
        **body.model_dump(),
        is_verified=True,  # 第一版直接通过
    )
    current_user.role = models.UserRole.expert
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/list", response_model=list[schemas.ExpertResp])
def list_experts(category: str = None, db: Session = Depends(get_db)):
    q = db.query(models.ExpertProfile).filter(models.ExpertProfile.is_verified == True)
    if category:
        q = q.filter(models.ExpertProfile.category == category)
    return q.all()


@router.get("/{expert_id}", response_model=schemas.ExpertResp)
def get_expert(expert_id: int, db: Session = Depends(get_db)):
    profile = db.query(models.ExpertProfile).filter(
        models.ExpertProfile.id == expert_id,
        models.ExpertProfile.is_verified == True,
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="专家不存在")
    return profile
