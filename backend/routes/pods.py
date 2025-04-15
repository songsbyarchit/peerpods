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
        media_type=pod_create.media_type,
        max_chars_per_message=pod_create.max_chars_per_message,
        max_messages_per_day=pod_create.max_messages_per_day,
        max_voice_message_seconds=pod_create.max_voice_message_seconds,
        launch_mode=pod_create.launch_mode,
        auto_launch_at=pod_create.auto_launch_at,
        timezone=pod_create.timezone,
        visibility="unlisted",  # optional — remove if schema sends it
        creator_id=creator.id
    )
    db.add(new_pod)
    db.commit()
    db.refresh(new_pod)
    return new_pod

@router.get("/preview")
def get_pod_previews(db: Session = Depends(get_db)):
    pods = db.query(models.Pod).all()
    previews = []

    for pod in pods:
        user_count = len({msg.user_id for msg in pod.messages})
        message_count = len(pod.messages)
        is_view_only = pod.state in ["locked", "launched"]
        remaining_slots = pod.max_messages_per_day - user_count if not is_view_only else 0

        preview = {
            "id": pod.id,
            "title": pod.title,
            "description": pod.description,
            "media_type": pod.media_type,
            "duration_hours": pod.duration_hours,
            "drift_tolerance": pod.drift_tolerance,
            "creator": pod.creator.username if pod.creator else "Unknown",
            "visibility": pod.visibility,
            "tags": pod.tags,
            "state": pod.state,
            "launch_mode": pod.launch_mode,
            "auto_launch_at": pod.auto_launch_at.isoformat() if pod.auto_launch_at else None,
            "message_count": message_count,
            "user_count": user_count,
            "remaining_slots": remaining_slots,
            "view_only": is_view_only
        }

        previews.append(preview)

    return previews