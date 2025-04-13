from backend.database import SessionLocal
from backend import models
import random

SAMPLE_USERS = [
    {"username": "deepthinker01", "bio": "Interested in ethics, philosophy, and consciousness."},
    {"username": "curiouscarla", "bio": "Learning about neuroscience, AI, and creativity."},
    {"username": "philosopherpete", "bio": "Exploring morality and decision-making frameworks."},
    {"username": "careerhopper", "bio": "Mid-career switcher, interested in meaningful work."},
]

SAMPLE_PODS = [
    {
        "title": "Ethics of AI",
        "description": "Discuss the moral implications of autonomous systems.",
        "duration_hours": 48,
        "drift_tolerance": 1
    },
    {
        "title": "Career Transitions",
        "description": "Share thoughts on pivoting careers with intention and reflection.",
        "duration_hours": 72,
        "drift_tolerance": 2
    },
    {
        "title": "Social Skills for Introspective People",
        "description": "How can introverts build confidence in social settings?",
        "duration_hours": 24,
        "drift_tolerance": 3
    }
]

SAMPLE_MESSAGES = [
    "I think about AI ethics mostly through the lens of responsibility and transparency.",
    "I changed careers twice — the hardest part was redefining my identity.",
    "Social confidence, for me, came from learning to listen more and speak less.",
]

def create_sample_data():
    db = SessionLocal()

    if db.query(models.User).first():
        print("Sample data already exists. Aborting.")
        return

    # Create users
    users = []
    for user in SAMPLE_USERS:
        u = models.User(username=user["username"], bio=user["bio"])
        db.add(u)
        users.append(u)

    db.commit()

    # Create pods
    pods = []
    for pod_data in SAMPLE_PODS:
        creator = random.choice(users)
        pod = models.Pod(
            title=pod_data["title"],
            description=pod_data["description"],
            duration_hours=pod_data["duration_hours"],
            drift_tolerance=pod_data["drift_tolerance"],
            creator_id=creator.id,
        )
        db.add(pod)
        pods.append(pod)

    db.commit()

    # Add messages
    for pod in pods:
        for _ in range(3):
            user = random.choice(users)
            content = random.choice(SAMPLE_MESSAGES)
            msg = models.Message(user_id=user.id, pod_id=pod.id, content=content)
            db.add(msg)

    db.commit()
    db.close()
    print("Sample data added.")

if __name__ == "__main__":
    create_sample_data()