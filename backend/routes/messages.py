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
from datetime import datetime, timezone

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
def send_message(
    pod_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    pod = db.query(models.Pod).filter(models.Pod.id == pod_id).first()
    if not pod:
        raise HTTPException(status_code=404, detail="Pod not found")

    # Check if pod is active based on time
    now = datetime.datetime.utcnow()
    launch = pod.auto_launch_at
    end = launch + datetime.timedelta(hours=pod.duration_hours) if launch else None

    if not (launch and launch <= now < end):
        raise HTTPException(status_code=403, detail="Pod is not active at this time")

    # Get user IDs who already sent messages in this pod
    participant_ids = {m.user_id for m in pod.messages}
    if current_user.id not in participant_ids and len(participant_ids) >= pod.max_messages_per_day:
        raise HTTPException(status_code=403, detail="Pod is full or you are not a participant")

    message = models.Message(
        content=content,
        media_type="text",
        user_id=current_user.id,
        pod_id=pod.id,
        created_at=datetime.now(timezone.utc)
    )

    db.add(message)
    db.commit()
    return {"message": "Message sent"}

@router.post("/pods/{pod_id}/send")
def send_message_to_active_pod(
    pod_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    from datetime import datetime, timedelta

    pod = db.query(models.Pod).filter(models.Pod.id == pod_id).first()
    if not pod:
        raise HTTPException(status_code=404, detail="Pod not found")

    if pod.state != "active":
        raise HTTPException(status_code=403, detail="Pod is not active")

    # Check if user is a participant
    participant_ids = {msg.user_id for msg in pod.messages}
    if current_user.id not in participant_ids:
        raise HTTPException(status_code=403, detail="You are not a participant of this pod")

    # Check daily message limit
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    user_messages_today = db.query(models.Message).filter(
        models.Message.pod_id == pod.id,
        models.Message.user_id == current_user.id,
        models.Message.created_at >= today_start
    ).count()

    if user_messages_today >= pod.max_messages_per_day:
        raise HTTPException(status_code=403, detail="Daily message limit reached for this pod")

    message = models.Message(
        content=content,
        media_type="text",
        user_id=current_user.id,
        pod_id=pod_id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(message)
    db.commit()
    return {"message": "Message sent"}