from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    messages = relationship("Message", back_populates="user")
    created_pods = relationship("Pod", back_populates="creator")

class Pod(Base):
    __tablename__ = "pods"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    duration_hours = Column(Integer, nullable=False)
    drift_tolerance = Column(Integer, default=3)  # 1–5 scale

    state = Column(String, default="created")  # created, configured, locked, launched, expired
    launch_mode = Column(String, default="manual")  # manual or countdown
    auto_launch_at = Column(DateTime, nullable=True)
    timezone = Column(String, default="UTC")

    media_type = Column(String, default="text")  # text, voice, both
    max_chars_per_message = Column(Integer, default=500)
    max_messages_per_day = Column(Integer, default=10)
    max_voice_message_seconds = Column(Integer, default=60)

    visibility = Column(String, default="unlisted")  # public, private, unlisted
    tags = Column(String, nullable=True)  # comma-separated values

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="created_pods")
    messages = relationship("Message", back_populates="pod")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=True)  # nullable=True for voice-only messages
    voice_path = Column(String, nullable=True)  # local path to the voice file

    media_type = Column(String, default="text")  # text or voice
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))
    pod_id = Column(Integer, ForeignKey("pods.id"))

    user = relationship("User", back_populates="messages")
    pod = relationship("Pod", back_populates="messages")