from pydantic import BaseModel
from typing import Optional, List
import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class PodCreate(BaseModel):
    title: str
    description: Optional[str] = None
    duration_hours: int
    drift_tolerance: int
    media_type: str
    max_chars_per_message: int
    max_messages_per_day: int
    max_voice_message_seconds: Optional[int] = None
    launch_mode: str
    auto_launch_at: Optional[datetime.datetime] = None
    timezone: str
    visibility: Optional[str] = "unlisted"
    tags: Optional[str] = None

class Pod(PodCreate):
    id: int
    creator_id: int

    class Config:
        orm_mode = True

class MessageBase(BaseModel):
    content: Optional[str] = None
    media_type: str  # "text" or "voice"
    voice_path: Optional[str] = None

class MessageCreate(MessageBase):
    pod_id: int
    user_id: int

class Message(MessageBase):
    id: int
    user_id: int
    pod_id: int

    class Config:
        orm_mode = True