import openai
import os
import json
from datetime import datetime, timedelta, timezone
from backend.database import SessionLocal
from backend import models
from dotenv import load_dotenv
import random

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

db = SessionLocal()

# Get existing pod titles to avoid duplicates
existing_titles = set(p.title.lower() for p in db.query(models.Pod).all())

def generate_pod_batch(existing_titles):
    system_prompt = (
        "You are helping design a platform for deep, intellectually curious conversations.\n"
        "Generate 50 unique, concise pod ideas. Each idea should:\n"
        "- Have a thought-provoking title (2–5 words max)\n"
        "- Include a one-line description (max 20 words)\n"
        "- Focus on complex, nuanced topics (e.g., consciousness, systems thinking, ethics, cognition, abstraction, metacognition)\n"
        "- Avoid overlap with these existing titles:\n"
        f"{', '.join(list(existing_titles)[:100])}"
    )

    user_prompt = "Generate the pod ideas in JSON format as a list of objects with `title` and `description` fields only."

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )

    try:
        content = response.choices[0].message.content
        json_start = content.find("[")
        json_text = content[json_start:]
        pod_ideas = json.loads(json_text)
        return pod_ideas
    except Exception as e:
        print("Failed to parse response:", e)
        return []

def insert_pods(pods, creator_id):
    for pod in pods:
        title = pod.get("title", "").strip()
        if title.lower() in existing_titles or not title:
            continue
        description = pod.get("description", "").strip() or "A pod for thoughtful discussion."

        new_pod = models.Pod(
            title=title,
            description=description,
            duration_hours=24,
            drift_tolerance=3,
            media_type="text",
            max_chars_per_message=250,
            max_messages_per_day=5,
            max_voice_message_seconds=60,
            launch_mode="auto",
            auto_launch_at=datetime.now(timezone.utc) + timedelta(hours=random.randint(1, 72)),
            timezone="Europe/London",
            visibility="unlisted",
            creator_id=creator_id,
            state="scheduled"
        )
        db.add(new_pod)
        existing_titles.add(title.lower())

for batch in range(20):
    print(f"Generating batch {batch + 1}/20...")
    creator = db.query(models.User).filter(models.User.username == "babyarchofficial").first()
    if not creator:
        raise Exception("User 'babyarchofficial' not found")
    pod_ideas = generate_pod_batch(existing_titles)
    insert_pods(pod_ideas, creator.id)
    db.commit()

db.close()
print("✅ 1000 synthetic scheduled pods generated.")