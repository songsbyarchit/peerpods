# backend/routes/messages.py

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