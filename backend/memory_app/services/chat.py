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
        scored.append({
            "content": memory.content,
            "score": float(score)
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]



def generate_response(query, chat_history=None):
    relevant_memories = retrieve_relevant_memories(query)

    formatted_memories = "\n".join(
        [f"- {m['content']}" if isinstance(m, dict) else f"- {m}" 
         for m in relevant_memories]
    )

    system_prompt = f"""
    You are an AI assistant with long-term memory.

    These are VERIFIED long-term facts about the user:
    {formatted_memories}

    IMPORTANT RULES:
    - Treat the above facts as TRUE.
    - Use them when answering.
    - Do NOT say you lack information if relevant facts are provided.
    - If the user asks follow-up questions like "Are you sure?",
    continue the conversation naturally.
    - Personalize the response using the stored facts when relevant.
    """

    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history if exists
    if chat_history:
        messages.extend(chat_history)

    messages.append({"role": "user", "content": query})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3
    )

    return response.choices[0].message.content, relevant_memories
