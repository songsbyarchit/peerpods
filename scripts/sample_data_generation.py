import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import SessionLocal
from backend import models
import random
from datetime import datetime

SAMPLE_USERS = [
    {"username": "deepthinker01", "bio": "Interested in ethics, philosophy, and consciousness."},
    {"username": "curiouscarla", "bio": "Learning about neuroscience, AI, and creativity."},
    {"username": "philosopherpete", "bio": "Exploring morality and decision-making frameworks."},
    {"username": "careerhopper", "bio": "Mid-career switcher, interested in meaningful work."},
    {"username": "flowfinder", "bio": "Focused on unlocking flow state through tech and music."},
]

SAMPLE_PODS = [
    {
        "title": "Ethics of AI",
        "description": "Discuss the moral implications of autonomous systems.",
        "duration_hours": 48,
        "drift_tolerance": 1,
        "media_type": "text",
    },
    {
        "title": "Career Transitions",
        "description": "Share thoughts on pivoting careers with intention and reflection.",
        "duration_hours": 72,
        "drift_tolerance": 2,
        "media_type": "both",
    },
    {
        "title": "Social Skills for Introspective People",
        "description": "How can introverts build confidence in social settings?",
        "duration_hours": 24,
        "drift_tolerance": 3,
        "media_type": "voice",
    },
    {
        "title": "Conscious Tech Design",
        "description": "Using tech to support mental health, not distract from it.",
        "duration_hours": 36,
        "drift_tolerance": 2,
        "media_type": "text",
    },
    {
        "title": "Philosophy of Flow",
        "description": "What does it really mean to be in flow?",
        "duration_hours": 60,
        "drift_tolerance": 4,
        "media_type": "both",
    },
]

SAMPLE_MESSAGES = [
    "I think about AI ethics mostly through the lens of responsibility and transparency.",
    "I changed careers twice — the hardest part was redefining my identity.",
    "Social confidence, for me, came from learning to listen more and speak less.",
    "Flow is a state where I lose the sense of time completely.",
    "Technology is only helpful when it aligns with human values.",
]

def create_sample_data():
    db = SessionLocal()

    db.query(models.Message).delete()
    db.query(models.Pod).delete()
    db.query(models.User).delete()
    db.commit()

    users = []
    for user in SAMPLE_USERS:
        u = models.User(username=user["username"], bio=user["bio"])
        db.add(u)
        users.append(u)

    db.commit()

    pods = []
    for pod_data in SAMPLE_PODS:
        creator = random.choice(users)
        pod = models.Pod(
            title=pod_data["title"],
            description=pod_data["description"],
            duration_hours=pod_data["duration_hours"],
            drift_tolerance=pod_data["drift_tolerance"],
            creator_id=creator.id,
            media_type=pod_data["media_type"],
            state="launched",
            launch_mode="manual",
            max_chars_per_message=500,
            max_messages_per_day=10,
            max_voice_message_seconds=60,
            timezone="UTC",
            visibility="unlisted",
            created_at=datetime.utcnow()
        )
        db.add(pod)
        pods.append(pod)

    db.commit()

    for pod in pods:
        for _ in range(5):
            user = random.choice(users)
            content = random.choice(SAMPLE_MESSAGES)
            msg = models.Message(
                user_id=user.id,
                pod_id=pod.id,
                content=content,
                media_type="text",
                created_at=datetime.utcnow()
            )
            db.add(msg)

    db.commit()
    db.close()
    print("Sample data added.")

if __name__ == "__main__":
    create_sample_data()