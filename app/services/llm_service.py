from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def generate_answer(context: str, question: str, history: list):

    system_prompt = """
You are a friendly conversational assistant that answers questions using a knowledge base.

The knowledge base is provided as DOCUMENT CONTEXT.

Core Rules:

1. The document context is the source of truth for factual information.
2. Do not invent facts that are not supported by the context.
3. You may explain information in a natural and conversational way.
4. If the context contains short statements, expand them slightly so they are easier to understand.
5. Never mention the words "context", "document", or "retrieval".
6. If the answer cannot be found in the context, say:
   "I could not find this information in the documents."

Conversation Behavior:

7. Use the conversation history to understand follow-up questions.
8. If the user asks things like:
   - "explain more"
   - "tell more"
   - "why"
   - "how"
   - "what about that"
   assume they are referring to the previous topic.
9. Continue the explanation of the same topic instead of asking the user again.

Response Style:

• If the question asks for a simple fact → answer briefly.
• If the question asks for explanation → give a clear explanation.
• Avoid filler phrases like "Sure", "I'd be happy to explain".
• Be natural and conversational.
"""

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # -------- ADD RECENT HISTORY --------
    for msg in history[-7:]:
        messages.append(msg)

    # -------- ADD CONTEXT --------
    messages.append({
        "role": "system",
        "content": f"Official Context:\n{context}"
    })

    # -------- USER QUESTION --------
    messages.append({
        "role": "user",
        "content": question
    })

    stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0,
    top_p=0.1,
    stream=True
    )

    for chunk in stream:

        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta

        if not delta:
            continue

        token = getattr(delta, "content", None)

        if token:
            yield token

def generate_rewrite(prompt: str):

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You rewrite user questions into short search queries for document retrieval."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        top_p=0.1
    )

    return completion.choices[0].message.content.strip()