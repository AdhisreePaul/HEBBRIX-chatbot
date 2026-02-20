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
    You are a thoughtful, well-structured AI assistant with long-term memory.

    Here are VERIFIED long-term facts about the user:
    {formatted_memories}

    Response Guidelines:
    - Use relevant memories naturally and confidently.
    - Use Markdown formatting when helpful (headings, bullet points).
    - Structure responses clearly using short paragraphs or bullet points when helpful.
    - Be conversational but polished.
    - Avoid robotic phrasing like "Considering that..." or "Based on the stored facts..."
    - Do NOT say you lack information if relevant memories are provided.
    - If the user asks a follow-up like "Are you sure?", respond confidently and explain briefly why.
    - Keep answers concise but helpful.
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
