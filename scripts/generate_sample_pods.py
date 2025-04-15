import sys, os, random
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

import openai
from openai import OpenAI

client = OpenAI()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import SessionLocal
from backend import models

openai.api_key = os.getenv("OPENAI_API_KEY")

POD_STATES = ["created", "configured", "locked", "launched", "expired"]
MEDIA_TYPES = ["text", "voice", "both"]
VISIBILITIES = ["public", "private", "unlisted"]
LAUNCH_MODES = ["manual", "countdown"]

def generate_title_and_description():
    prompt = "Suggest a unique title and one-sentence description for a discussion pod focused on thoughtful conversation topics."
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{ "role": "user", "content": prompt }],
        max_tokens=80,
        temperature=0.9
    )
    reply = res.choices[0].message.content
    lines = reply.strip().split("\n")
    title = lines[0].replace("Title:", "").strip() if "Title:" in lines[0] else lines[0].strip()
    desc = lines[1].replace("Description:", "").strip() if len(lines) > 1 else "Thought-provoking discussion."
    return title, desc

def generate_message_content(topic):
    prompt = f"Write a short thoughtful comment in 1–2 sentences on the topic: '{topic}'"
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{ "role": "user", "content": prompt }],
        max_tokens=60,
        temperature=0.8
    )
    return res.choices[0].message.content.strip()

def create_pods(n=40):
    db = SessionLocal()
    users = db.query(models.User).all()
    if not users:
        print("No users found. Add users before generating pods.")
        return

    for _ in range(n):
        title, description = generate_title_and_description()
        creator = random.choice(users)
        state = random.choice(POD_STATES)
        media_type = random.choice(MEDIA_TYPES)
        launch_mode = random.choice(LAUNCH_MODES)
        auto_launch_at = None
        if launch_mode == "countdown":
            auto_launch_at = datetime.utcnow() + timedelta(hours=random.randint(1, 24))

        pod = models.Pod(
            title=title,
            description=description,
            duration_hours=random.choice([24, 48, 72]),
            drift_tolerance=random.randint(1, 5),
            creator_id=creator.id,
            state=state,
            launch_mode=launch_mode,
            auto_launch_at=auto_launch_at,
            media_type=media_type,
            max_chars_per_message=random.choice([100, 250, 500, 1000]),
            max_messages_per_day=random.choice([3, 5, 10, 20]),
            max_voice_message_seconds=random.choice([30, 60, 90]),
            visibility=random.choice(VISIBILITIES),
            created_at=datetime.utcnow()
        )
        db.add(pod)
        db.commit()
        db.refresh(pod)

        message_count = random.randint(3, 20)
        msg_users = random.sample(users, min(len(users), random.randint(1, 5)))
        for _ in range(message_count):
            user = random.choice(msg_users)
            content = generate_message_content(title)
            msg = models.Message(
                user_id=user.id,
                pod_id=pod.id,
                content=content,
                media_type="text",  # keep it simple for now
                created_at=datetime.utcnow()
            )
            db.add(msg)

        db.commit()
        print(f"Created pod: {title} with {message_count} messages.")

    db.close()

if __name__ == "__main__":
    create_pods(n=40)