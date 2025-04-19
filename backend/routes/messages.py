# backend/routes/messages.py
from backend.models import User, Pod, Message
from backend.dependencies.jwt import get_current_user
import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
import os
import uuid
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
def create_message(
    user_id: int = Form(...),
    pod_id: int = Form(...),
    media_type: str = Form(...),  # "text" or "voice"
    content: str = Form(None),
    voice_file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    pod = db.query(models.Pod).filter(models.Pod.id == pod_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if not pod:
        raise HTTPException(status_code=404, detail="Pod not found.")

    voice_path = None

    if media_type == "voice":
        if voice_file is None:
            raise HTTPException(status_code=400, detail="Voice file missing.")

        folder = "voice_notes"
        os.makedirs(folder, exist_ok=True)

        extension = os.path.splitext(voice_file.filename)[1]
        filename = f"{uuid.uuid4()}{extension}"
        path = os.path.join(folder, filename)

        with open(path, "wb") as f:
            f.write(voice_file.file.read())

        voice_path = path
        content = None

    new_msg = models.Message(
        user_id=user.id,
        pod_id=pod.id,
        content=content,
        voice_path=voice_path,
        media_type=media_type
    )

    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg

@router.post("/pods/{pod_id}/messages")
def send_message(pod_id: int, content: str = Form(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pod = db.query(Pod).filter(Pod.id == pod_id).first()
    if not pod:
        raise HTTPException(status_code=404, detail="Pod not found")
    if not pod.is_active:
        raise HTTPException(status_code=403, detail="Cannot send message to an inactive pod")

    # Count distinct pods this user has messaged in
    joined_pod_ids = db.query(Message.pod_id).filter(Message.user_id == current_user.id).distinct().all()
    joined_pod_ids = {pid for (pid,) in joined_pod_ids}

    if pod_id not in joined_pod_ids and len(joined_pod_ids) >= 3:
        raise HTTPException(status_code=403, detail="You can only join 3 pods")

    message = Message(
        content=content,
        media_type="text",
        user_id=current_user.id,
        pod_id=pod_id,
        created_at=datetime.datetime.utcnow()
    )
    db.add(message)
    db.commit()
    return {"message": "Message sent"}