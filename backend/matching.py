def compute_similarity(text1: str, text2: str) -> int:
    """
    Simple similarity score based on word overlap.
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    overlap = words1.intersection(words2)
    return len(overlap)

def match_pods_for_user(user_bio: str, pod_list: list, top_n: int = 3) -> list:
    """
    Returns top N matching pods for a user based on bio similarity.
    Each pod is expected to have a 'description' attribute.
    """
    scored = []
    for pod in pod_list:
        score = compute_similarity(user_bio, pod.description or "")
        scored.append((pod, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [pod for pod, _ in scored[:top_n]]