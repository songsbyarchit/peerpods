from pydantic import BaseModel
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class PodBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration_hours: int
    drift_tolerance: int

class PodCreate(PodBase):
    pass

class Pod(PodBase):
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