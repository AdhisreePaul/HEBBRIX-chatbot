from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def extract_memories(text):
    prompt = f"""
Extract only durable user facts from this conversation.
Ignore temporary requests.
Return each fact as a separate line.

Conversation:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}]
    )

    output = response.choices[0].message.content
    facts = [line.strip("- ").strip() for line in output.split("\n") if line.strip()]
    return facts
