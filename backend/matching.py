import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()

def get_embedding(text: str) -> list:
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def match_pods_for_user(user_bio: str, pod_list: list, top_n: int = 3) -> list:
    if not user_bio or not pod_list:
        return []

    user_vec = get_embedding(user_bio)
    scored = []
    for pod in pod_list:
        combined = f"{pod.title or ''} {pod.description or ''}"
        pod_vec = get_embedding(combined)
        score = cosine_similarity(user_vec, pod_vec)
        scored.append((pod, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [pod for pod, _ in scored[:top_n]]