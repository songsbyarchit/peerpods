# backend/routes/messages.py

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
def get_all_messages(db: Session = Depends(get_db)):
    return db.query(models.Message).all()

@router.post("/")
def create_message(msg_create: schemas.MessageCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == msg_create.user_id).first()
    pod = db.query(models.Pod).filter(models.Pod.id == msg_create.pod_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if not pod:
        raise HTTPException(status_code=404, detail="Pod not found.")

    new_msg = models.Message(
        user_id=user.id,
        pod_id=pod.id,
        content=msg_create.content
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg