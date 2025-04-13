# backend/routes/users.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import models, schemas
from backend.database import SessionLocal
from backend.matching import match_pods_for_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_all_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.post("/")
def create_user(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    # Create a new user
    new_user = models.User(username=user_create.username, bio=user_create.bio)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{user_id}/recommended")
def get_recommended_pods(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    all_pods = db.query(models.Pod).all()

    # Use the matching logic
    recommended = match_pods_for_user(user.bio or "", all_pods, top_n=3)
    return recommended