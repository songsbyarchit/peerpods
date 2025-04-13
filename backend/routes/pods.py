# backend/routes/pods.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import models, schemas
from backend.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_all_pods(db: Session = Depends(get_db)):
    return db.query(models.Pod).all()

@router.post("/")
def create_pod(pod_create: schemas.PodCreate, db: Session = Depends(get_db)):
    # For now, let the first user (id=1) be the creator if none specified
    creator = db.query(models.User).first()
    if not creator:
        raise HTTPException(status_code=400, detail="No users in database to assign as creator.")

    new_pod = models.Pod(
        title=pod_create.title,
        description=pod_create.description,
        duration_hours=pod_create.duration_hours,
        drift_tolerance=pod_create.drift_tolerance,
        creator_id=creator.id
    )
    db.add(new_pod)
    db.commit()
    db.refresh(new_pod)
    return new_pod