# backend/routes/users.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import models, schemas
from backend.auth import hash_password
from backend.database import SessionLocal
from backend.matching import match_pods_for_user
from backend.dependencies.jwt import get_current_user
from backend.dependencies.db import get_db

router = APIRouter()

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

@router.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists.")

    new_user = models.User(
        username=user.username,
        bio=user.bio,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username}

@router.patch("/me")
def update_user_bio(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    bio = payload.get("bio")
    if bio is None:
        raise HTTPException(status_code=400, detail="Missing 'bio' in request")

    # Re-fetch the user in the current session
    user = db.query(models.User).filter_by(id=current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.bio = bio
    db.commit()
    db.refresh(user)
    return {"bio": user.bio}