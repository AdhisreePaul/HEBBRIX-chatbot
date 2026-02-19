from openai import OpenAI
from django.conf import settings
from .embedding import get_embedding, cosine_similarity
from memory_app.models import Memory

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def retrieve_relevant_memories(query, top_k=3):
    query_embedding = get_embedding(query)
    memories = Memory.objects.all()

    scored = []
    for memory in memories:
        score = cosine_similarity(query_embedding, memory.embedding)
        scored.append((score, memory.content))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [m for _, m in scored[:top_k]]


def generate_response(query):
    relevant_memories = retrieve_relevant_memories(query)

    prompt = f"""
You are a helpful AI assistant.

Relevant user memories:
{relevant_memories}

User question:
{query}

Answer in a personalized way using the memories if relevant.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content, relevant_memories
