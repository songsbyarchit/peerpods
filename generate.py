import os, random, time, datetime, json
from collections import defaultdict
from faker import Faker
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import openai
from openai import OpenAI
from backend.database import SessionLocal
from backend import models
from backend.routes.pods import refresh_pod_states
from pathlib import Path

# --------------------------------------------------
# ENV / INITIALISE
# --------------------------------------------------
load_dotenv()
print("📄 .env DATABASE_URL value:", os.getenv("DATABASE_URL"))
print(f"🔍 Using .env from: {Path('.env').resolve()}")
env_db = os.getenv("DATABASE_URL")
if not env_db:
    raise Exception("❌ DATABASE_URL not found in .env or environment.")
os.environ["DATABASE_URL"] = env_db
DATABASE_URL = env_db
openai.api_key = os.getenv("OPENAI_API_KEY")
print(f"✅ .env forced: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
faker = Faker()
Faker.seed(42)
print(f"🔗 Connected to: {engine.url}\n")

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def unique_bio(existing_bios: set[str]) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    for _ in range(10):
        prompt = (
            "Generate a short, thoughtful one-line bio for a curious thinker who likes ideas, "
            "debate, and meaningful conversation. Avoid clichés."
        )
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        candidate = resp.choices[0].message.content.strip()
        lower = candidate.lower()
        if all(sw not in lower for sw in existing_bios):
            return candidate
    return "Curious about the world and always exploring new ideas."

def pick_participants(users, creator_id, min_p=2, max_p=7):
    pool = [u for u in users if u.id != creator_id]
    num = random.randint(min_p, max_p)
    return random.sample(pool, num)

def turbo_completion(prompt: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return resp.choices[0].message.content.strip()

# --------------------------------------------------
# MAIN GENERATION
# --------------------------------------------------

def seed_users(session, target=100):
    existing = session.query(models.User).all()
    bios = {u.bio.lower() for u in existing if u.bio}

    while len(existing) < target:
        username = faker.unique.user_name()[:30]
        bio = unique_bio(bios)
        usr = models.User(
            username=username,
            hashed_password="$2b$12$placeholderhash",
            bio=bio,
            is_admin=False,
        )
        session.add(usr)
        session.flush()
        bios.add(bio.lower())
        existing.append(usr)

    session.commit()
    return existing

def seed_pods(session, users):
    part_map: defaultdict[int, set[int]] = defaultdict(set)
    for m in session.query(models.Message).all():
        part_map[m.user_id].add(m.pod_id)
    for p in session.query(models.Pod).all():
        part_map[p.creator_id].add(p.id)

    duration_options = [24, 168, 720]
    state_ratio = [0.3, 0.4, 0.3]
    now = datetime.datetime.now(datetime.timezone.utc)

    while True:
        eligible = [u for u in users if len(part_map[u.id]) < 10]
        if not eligible:
            break
        user = random.choice(eligible)

        r = random.random()
        if r < state_ratio[0]:
            launch_at = now - datetime.timedelta(hours=random.randint(48, 240))
            status = "expired"
        elif r < state_ratio[0] + state_ratio[1]:
            launch_at = now - datetime.timedelta(hours=random.randint(1, 12))
            status = "active"
        else:
            launch_at = now + datetime.timedelta(hours=random.randint(1, 72))
            status = "scheduled"

        duration = random.choice(duration_options)
        existing_titles = {p.title.lower().strip() for p in session.query(models.Pod).all()}
        generated_title = None
        categories = [
            "ethics", "personal habits", "modern relationships", "technological dilemmas", 
            "economic trends", "philosophy of mind", "history", "education", 
            "political structures", "art and creativity"
        ]
        topic_hint = random.choice(categories)
        for _ in range(5):
            prompt = (
                f"Suggest a short, clear, and grammatically correct title for a small group discussion "
                f"related to the topic of '{topic_hint}'. The title should be under 8 words. "
                "It must sound natural, specific, and non-generic. Avoid repetition or resemblance to any of these titles: "
                f"{list(existing_titles)}. Avoid buzzwords like sustainability, climate, or future."
            )
            resp = OpenAI(api_key=os.getenv("OPENAI_API_KEY")).chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.85,
            )
            candidate = resp.choices[0].message.content.strip()
            if candidate and candidate.lower() not in existing_titles and len(candidate.split()) <= 8:
                generated_title = candidate
                break

        if not generated_title:
            raise ValueError("Failed to generate a unique and valid title after 5 attempts.")

        desc_prompt = (
            f"Write a MAXIMUM 20-word description expanding on the topic: '{generated_title}'. "
            "Make it specific and realistic. Mention how someone's opinion might be strong, unsure, or has shifted over time."
        )

        generated_description = None
        for _ in range(5):
            desc_resp = OpenAI(api_key=os.getenv("OPENAI_API_KEY")).chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": desc_prompt}],
                temperature=0.85,
            )
            candidate = desc_resp.choices[0].message.content.strip()
            if candidate and 10 <= len(candidate.split()) <= 25:
                generated_description = candidate
                break

        if not generated_description:
            print(f"⚠️ Failed to generate good description for title: '{generated_title}'. Using fallback.")
            generated_description = f"A discussion on '{generated_title}' with different points of view shared thoughtfully."


        pod = models.Pod(
            title=generated_title,
            description=generated_description,
            duration_hours=duration,
            drift_tolerance=random.randint(1, 5),
            media_type="text",
            max_chars_per_message=500,
            max_messages_per_day=10,
            max_voice_message_seconds=60,
            launch_mode="countdown",
            auto_launch_at=launch_at,
            timezone="UTC",
            visibility="unlisted",
            creator_id=user.id,
            tags="seeded",
        )
        session.add(pod)
        session.flush()
        part_map[user.id].add(pod.id)

        print(f"   🌐 Pod: '{pod.title}' ({status}, {duration}h)")

        participants = pick_participants(users, creator_id=user.id)
        all_participants = [user] + participants

        for participant in participants:
            part_map[participant.id].add(pod.id)

        start_ts = launch_at + datetime.timedelta(minutes=1)
        for i in range(random.randint(6, 15)):
            speaker = random.choice(all_participants)
            prior_messages = session.query(models.Message).filter_by(pod_id=pod.id).order_by(models.Message.created_at).all()
            context = [
                {"role": "system", "content": f"You're a thoughtful participant in a discussion on '{pod.title}'."}
            ]

            for m in prior_messages:
                context.append({"role": "user", "content": m.content})

            tone = random.choice([
                "neutral and balanced",
                "curious and probing",
                "humorous and light",
                "concise and direct",
                "reflective and philosophical"
            ])

            feature = random.choice([
                "ask a thought-provoking question",
                "agree with a previous idea briefly",
                "offer a gentle challenge to a point made",
                "add a new perspective without repeating others",
                "clarify a subtle distinction between ideas"
            ])

            context.append({
                "role": "user",
                "content": (
                    f"{speaker.username} is replying next. "
                    f"Write a thoughtful, realistic message (25–120 words) in a {tone} tone. "
                    f"As part of the message, try to {feature}, but don’t make it the whole message."
                )
            })
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=context,
                temperature=0.8
            )
            content = resp.choices[0].message.content.strip()
            msg = models.Message(
                content=content,
                media_type="text",
                user_id=speaker.id,
                pod_id=pod.id,
                created_at=start_ts,
            )
            session.add(msg)
            print(f"      🗣️ {speaker.username}: {content[:40]}…")
            start_ts += datetime.timedelta(minutes=random.randint(2, 10))

        session.commit()
        refresh_pod_states(session)
        session.commit()

# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------
if __name__ == "__main__":
    sess = Session()
    print("🌱  Seeding users …")
    users = seed_users(sess, 100)
    print("🌱  Seeding pods & messages …")
    seed_pods(sess, users)
    sess.close()
    print("\n✅  Done. 100 users, each ≤10 pods with coherent messages (expired, active, scheduled).")