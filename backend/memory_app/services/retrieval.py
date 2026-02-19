import numpy as np
from .embedding import get_embedding, cosine_similarity


def keyword_overlap(query, memory):
    query_words = set(query.lower().split())
    memory_words = set(memory.lower().split())
    return len(query_words.intersection(memory_words))


def hybrid_search(query, memories, alpha=0.8):
    """
    alpha = weight for semantic similarity
    (1 - alpha) = weight for keyword overlap
    """

    query_embedding = get_embedding(query)

    scored = []

    for memory in memories:
        semantic_score = cosine_similarity(query_embedding, memory.embedding)
        keyword_score = keyword_overlap(query, memory.content)

        final_score = alpha * semantic_score + (1 - alpha) * keyword_score

        scored.append((final_score, memory))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [m for _, m in scored[:3]]
