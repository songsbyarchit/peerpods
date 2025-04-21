import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str) -> list:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[text]
    )
    return response.data[0].embedding

def get_batch_embeddings(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [r.embedding for r in response.data]

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def match_pods_for_user(user_bio: str, pod_list: list, top_n: int = 3) -> list:
    if not user_bio or not pod_list:
        return []

    user_vec = get_embedding(user_bio)
    scored = []

    pod_texts = [f"{pod.title or ''} {pod.description or ''}" for pod in pod_list]
    pod_vectors = get_batch_embeddings(pod_texts)
    pod_vectors_np = np.array(pod_vectors)
    user_vec_np = np.array(user_vec)
    dot_products = np.dot(pod_vectors_np, user_vec_np)
    norms = np.linalg.norm(pod_vectors_np, axis=1) * np.linalg.norm(user_vec_np)
    similarities = dot_products / norms

    for pod, score in zip(pod_list, similarities):
        relevance = min(100, int(60 + (score + 1) * 20))
        pod.relevance = relevance
        scored.append(pod)

    scored.sort(key=lambda pod: pod.relevance, reverse=True)
    return scored[:top_n]