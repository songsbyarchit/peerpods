import os
import random
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from faker import Faker
from openai import OpenAI
import openai

from backend.models import User, Pod, Message  # Use correct import paths

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
faker = Faker()

def pick_random_users(session, min_users=3, max_users=5):
    users = session.query(User).all()
    if len(users) < min_users:
        raise ValueError("Not enough users.")
    return random.sample(users, random.randint(min_users, max_users))

def generate_conversation_messages(user_objs, num_messages):
    messages = []
    context = ""
    for i in range(num_messages):
        user = random.choice(user_objs)
        prompt = f"""This is a deep conversation between users. Previous messages:\n{context}\n\nNow write a reply from {user.username}:"""
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        msg = response.choices[0].message.content.strip()
        msg = response.choices[0].message.content.strip()
        context += f"{user.username}: {msg}\n"
        messages.append((user, msg))
    return messages

def create_pod_with_messages(session):
    users = pick_random_users(session)
    num_messages = random.randint(5, 15)
    messages_data = generate_conversation_messages(users, num_messages)

    creator = random.choice(users)
    pod = Pod(
        title=faker.sentence(nb_words=4),
        description=faker.paragraph(),
        duration_hours=random.choice([24, 168]),
        drift_tolerance=random.randint(1, 5),
        state="launched",
        launch_mode="manual",
        timezone="UTC",
        media_type="text",
        max_chars_per_message=500,
        max_messages_per_day=10,
        max_voice_message_seconds=60,
        visibility="unlisted",
        tags="ai,generated,discussion",
        creator_id=creator.id,
        created_at=faker.date_time_between(start_date="-3d", end_date="now")
    )
    session.add(pod)
    session.commit()
    session.refresh(pod)

    start_time = faker.date_time_between(start_date="-3d", end_date="now")
    time_increment = datetime.timedelta(minutes=random.randint(1, 10))

    for user, content in messages_data:
        message_time = start_time
        start_time += datetime.timedelta(minutes=random.randint(3, 12))  # simulate gap between messages
        message = Message(
            content=content,
            media_type="text",
            user_id=user.id,
            pod_id=pod.id,
            created_at=message_time
        )
        session.add(message)

    session.commit()
    print(f"✅ Created pod '{pod.title}' with {len(messages_data)} messages.")

if __name__ == "__main__":
    create_pod_with_messages(session)