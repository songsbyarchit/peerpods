# backend/routes/pods.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import models, schemas
from backend.database import SessionLocal
from backend.dependencies.jwt import get_current_user
from sqlalchemy import or_
from typing import List, Optional
from backend import models
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_all_pods(db: Session = Depends(get_db)):
    pods = db.query(models.Pod).all()
    result = []

    for pod in pods:
        messages = [
            {
                "media_type": m.media_type,
                "content": m.content,
                "voice_path": m.voice_path,
                "user": m.user.username if m.user else "Unknown"
            }
            for m in pod.messages
        ]

        result.append({
            "id": pod.id,
            "title": pod.title,
            "description": pod.description,
            "media_type": pod.media_type,
            "messages": messages,
            "creator": pod.creator.username if pod.creator else "Unknown",
            "duration_hours": pod.duration_hours,
            "drift_tolerance": pod.drift_tolerance,
            "visibility": pod.visibility,
            "tags": pod.tags,
            "state": pod.state,
            "launch_mode": pod.launch_mode,
            "auto_launch_at": pod.auto_launch_at.isoformat() if pod.auto_launch_at else None,
        })

    return result

@router.post("/")
def create_pod(
    pod_create: schemas.PodCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    creator = current_user
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

@router.get("/mine")
def get_user_pods(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Pod).filter(models.Pod.creator_id == current_user.id).all()

@router.get("/user")
def get_user_pods(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Pod).filter(models.Pod.creator_id == current_user.id).all()

@router.get("/recommended")
def get_recommended_pods(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    pods = db.query(models.Pod).filter(models.Pod.state != "locked").all()

    def tokenize(text):
        return set(word.lower() for word in text.split() if len(word) > 2)

    user_keywords = tokenize(current_user.bio or "")

    scored_pods = []
    for pod in pods:
        user_ids = {msg.user_id for msg in pod.messages}
        remaining_slots = pod.max_messages_per_day - len(user_ids)
        if remaining_slots <= 0:
            continue

        pod_text = f"{pod.title} {pod.description or ''}"
        pod_keywords = tokenize(pod_text)
        overlap = user_keywords.intersection(pod_keywords)
        score = len(overlap)

        pod_data = pod.__dict__.copy()
        pod_data["remaining_slots"] = remaining_slots
        pod_data["score"] = score
        scored_pods.append(pod_data)

    scored_pods.sort(key=lambda p: p["score"], reverse=True)
    return scored_pods

@router.get("/active")
def get_active_pods(db: Session = Depends(get_db)):
    pods = db.query(models.Pod).filter(models.Pod.state.in_(["configured", "launched"])).all()
    result = []
    for pod in pods:
        messages = [
            {
                "media_type": m.media_type,
                "content": m.content,
                "voice_path": m.voice_path,
            }
            for m in pod.messages
        ]
        result.append({
            "id": pod.id,
            "title": pod.title,
            "messages": messages
        })
    return result

@router.get("/stats")
def get_app_stats(db: Session = Depends(get_db)):
    total_messages = db.query(models.Message).count()

    voice_message_count = db.query(models.Message).filter(models.Message.media_type == "voice").count()
    total_voice_minutes = voice_message_count  # Assuming 1 minute per voice message

    return {
        "totalMessages": total_messages,
        "totalVoiceMinutes": total_voice_minutes
    }

@router.get("/pod/{pod_id}")
def get_pod_by_id(pod_id: int, db: Session = Depends(get_db)):
    pod = db.query(models.Pod).filter(models.Pod.id == pod_id).first()
    if not pod:
        raise HTTPException(status_code=404, detail="Pod not found")

    messages = [
        {
            "media_type": m.media_type,
            "content": m.content,
            "voice_path": m.voice_path,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "user": m.user.username if m.user else "Unknown"
        }
        for m in pod.messages
    ]

    return {
        "id": pod.id,
        "title": pod.title,
        "description": pod.description,
        "media_type": pod.media_type,
        "messages": messages,
        "creator": pod.creator.username if pod.creator else "Unknown",
        "duration_hours": pod.duration_hours,
        "drift_tolerance": pod.drift_tolerance,
        "visibility": pod.visibility,
        "tags": pod.tags,
        "state": pod.state,
        "launch_mode": pod.launch_mode,
        "auto_launch_at": pod.auto_launch_at.isoformat() if pod.auto_launch_at else None,
    }

@router.post("/refresh-states")
def refresh_pod_states(db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    pods = db.query(models.Pod).all()

    for pod in pods:
        if pod.auto_launch_at:
            launch_time = pod.auto_launch_at
            expiry_time = launch_time + timedelta(hours=pod.duration_hours)

            if now < launch_time:
                pod.state = "scheduled"
            elif launch_time <= now < expiry_time:
                pod.state = "active"
            else:
                pod.state = "expired"

    db.commit()
    return {"detail": "Pod states refreshed"}

@router.get("/search")
def search_pods(
    query: str,
    state: Optional[str] = None,
    media: Optional[str] = None,
    sort: Optional[str] = None,
    db: Session = Depends(get_db)
):
    base_query = db.query(models.Pod).filter(
        or_(
            models.Pod.title.ilike(f"%{query}%"),
            models.Pod.description.ilike(f"%{query}%")
        )
    )

    if state:
        base_query = base_query.filter(models.Pod.state == state)
    if media:
        base_query = base_query.filter(models.Pod.media_type == media)

    pods = base_query.all()

    if sort == "messages":
        pods.sort(key=lambda pod: len(pod.messages), reverse=True)
    elif sort == "latest":
        pods.sort(key=lambda pod: max((m.created_at for m in pod.messages), default=datetime.min), reverse=True)
    elif sort == "duration":
        pods.sort(key=lambda pod: pod.duration_hours, reverse=True)

    results = []
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

        results.append(preview)

    return results