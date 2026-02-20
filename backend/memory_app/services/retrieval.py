import numpy as np
from .embedding import get_embedding, cosine_similarity


def keyword_overlap_score(query: str, memory_text) -> float:
    """
    Compute normalized keyword overlap score between query and memory.
    Returns a value between 0 and 1.
    """

    # 🔒 Defensive conversion to string
    if not isinstance(query, str):
        query = str(query)

    if not isinstance(memory_text, str):
        memory_text = str(memory_text)

    query_words = set(query.lower().split())
    memory_words = set(memory_text.lower().split())

    if not query_words:
        return 0.0

    overlap = query_words.intersection(memory_words)

    return len(overlap) / len(query_words)


def hybrid_rank_memories(query: str, memories, 
                         alpha: float = 0.7,
                         beta: float = 0.2,
                         gamma: float = 0.1):
    """
    Hybrid ranking combining:
    - Semantic similarity (alpha)
    - Keyword overlap (beta)
    - Importance score (gamma)

    alpha + beta + gamma should sum to 1.
    """

    query_embedding = get_embedding(query)

    results = []

    for memory in memories:

        # 1️⃣ Semantic similarity
        semantic_score = cosine_similarity(
            query_embedding,
            memory.embedding
        )

        # Normalize cosine similarity from [-1,1] to [0,1]
        semantic_score = (semantic_score + 1) / 2

        # 2️⃣ Keyword overlap (already normalized)
        keyword_score = keyword_overlap_score(query, memory.content)

        # 3️⃣ Importance score (assumed already between 0 and 1)
        importance_score = memory.importance_score or 0.0

        # 4️⃣ Final weighted score
        final_score = (
            alpha * semantic_score +
            beta * keyword_score +
            gamma * importance_score
        )

        results.append({
            "id": memory.id,
            "content": memory.content,
            "semantic_score": round(semantic_score, 4),
            "keyword_score": round(keyword_score, 4),
            "importance_score": round(importance_score, 4),
            "final_score": round(final_score, 4)
        })

    # Sort by final score descending
    results.sort(key=lambda x: x["final_score"], reverse=True)

    return results