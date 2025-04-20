# backend/routes/pods.py

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session, aliased
from backend import models, schemas
from backend.database import SessionLocal
from backend.dependencies.jwt import get_current_user
from sqlalchemy import or_
from typing import List, Optional
from backend import models
from datetime import datetime
from backend.matching import match_pods_for_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_all_pods(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
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
            "is_creator": current_user.id == pod.creator_id if current_user else False,
            "is_participant": current_user.id in {m.user_id for m in pod.messages},
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

@router.get("/user-full")
def get_user_pods_full(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    all_pods = db.query(models.Pod).all()
    user_pods = []
    for pod in all_pods:
        participant_ids = {m.user_id for m in pod.messages}
        if current_user.id == pod.creator_id or current_user.id in participant_ids:
            user_pods.append({
                "id": pod.id,
                "title": pod.title,
                "state": pod.state,
                "is_creator": current_user.id == pod.creator_id,
                "is_participant": current_user.id in participant_ids,
                "auto_launch_at": pod.auto_launch_at.isoformat() if pod.auto_launch_at else None,
                "duration_hours": pod.duration_hours
            })
    return user_pods

@router.post("/update-bio")
def update_bio(bio: str = Form(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    current_user.bio = bio
    db.commit()
    db.refresh(current_user)
    return {"message": "Bio updated successfully", "bio": current_user.bio}

@router.get("/recommended")
def get_recommended_pods(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    pods = db.query(models.Pod).filter(models.Pod.state != "locked").all()

    available = []
    now = datetime.utcnow()
    for pod in pods:
        user_ids = {msg.user_id for msg in pod.messages}
        remaining_slots = pod.max_messages_per_day - len(user_ids)
        has_not_started = pod.auto_launch_at and pod.auto_launch_at > now
        if remaining_slots > 0 and has_not_started:
            pod.remaining_slots = remaining_slots
            available.append(pod)

    matched = match_pods_for_user(current_user.bio or "", available)

    # convert matched pods to dict for response
    return [
        {
            "id": pod.id,
            "title": pod.title,
            "description": pod.description,
            "media_type": pod.media_type,
            "duration_hours": pod.duration_hours,
            "drift_tolerance": pod.drift_tolerance,
            "visibility": pod.visibility,
            "tags": pod.tags,
            "state": pod.state,
            "launch_mode": pod.launch_mode,
            "auto_launch_at": pod.auto_launch_at.isoformat() if pod.auto_launch_at else None,
            "remaining_slots": pod.remaining_slots,
            "relevance": pod.relevance
        }
        for pod in matched
    ]

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
    total_messages = db.query(models.Message).count() or 0

    voice_message_count = db.query(models.Message).filter(models.Message.media_type == "voice").count() or 0
    total_voice_minutes = voice_message_count * 1  # Placeholder: 1 minute per voice message

    pod_count = db.query(models.Pod).count() or 0
    user_count = db.query(models.User).count() or 0

    return {
        "totalMessages": int(total_messages),
        "totalVoiceMinutes": int(total_voice_minutes),
        "totalPods": int(pod_count),
        "totalUsers": int(user_count)
    }

@router.get("/pod/{pod_id}")
def get_pod_by_id(
    pod_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
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

    participant_ids = {m.user_id for m in pod.messages}
    can_send = current_user.id == pod.creator_id or current_user.id in participant_ids

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
        "can_send": can_send
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
    MessageUser = aliased(models.User)

    base_query = db.query(models.Pod)\
        .join(models.User, models.Pod.creator)\
        .outerjoin(models.Message, models.Message.pod_id == models.Pod.id)\
        .outerjoin(MessageUser, models.Message.user_id == MessageUser.id)\
        .filter(
            or_(
                models.Pod.title.ilike(f"%{query}%"),
                models.Pod.description.ilike(f"%{query}%"),
                models.User.username.ilike(f"%{query}%"),
                MessageUser.username.ilike(f"%{query}%")
            )
        ).distinct()

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