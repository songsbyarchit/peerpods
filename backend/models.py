from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    messages = relationship("Message", back_populates="user")
    created_pods = relationship("Pod", back_populates="creator")

class Pod(Base):
    __tablename__ = "pods"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    duration_hours = Column(Integer, nullable=False)
    drift_tolerance = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="created_pods")
    messages = relationship("Message", back_populates="pod")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))
    pod_id = Column(Integer, ForeignKey("pods.id"))

    user = relationship("User", back_populates="messages")
    pod = relationship("Pod", back_populates="messages")