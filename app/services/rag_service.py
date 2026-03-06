from app.services.embedding_service import get_embedding
from app.core.qdrant_client import client
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.services.llm_service import generate_answer, generate_rewrite
from app.services.memory_service import get_history, save_history
from app.services.retrieval_service import retrieve_chunks
from app.core.constants import (
    COLLECTION_NAME,
    MAX_CONTEXT_CHUNKS,
    MAX_CONTEXT_LENGTH,
    KEYWORD_SCROLL_LIMIT,
    SCORE_THRESHOLD
)


def rewrite_query(question: str, history: list):

    recent_history = history[-4:]

    history_text = ""
    for msg in recent_history:
        history_text += f"{msg['role']}: {msg['content']}\n"

    prompt = f"""
You generate search queries for a document retrieval system.

Use the conversation history to understand the user's current question.

If the user asks a follow-up question like:
- explain more
- tell more
- why
- how
- what about that

assume it refers to the previous topic in the conversation.

Conversation history:
{history_text}

User question:
{question}

Generate 3 short search queries that best represent the user's intent.

Rules:
- Preserve the meaning of the question
- Use the previous topic if the question is a follow-up
- Do not introduce new topics
- Each query should be short

Return only the queries, one per line.
"""

    result = generate_rewrite(prompt)

    queries = []

    for line in result.split("\n"):
        q = line.strip()
        if q:
            queries.append(q)

    queries.insert(0, question)

    queries = list(dict.fromkeys(queries))[:4]

    return queries

def answer_question(session_id: str, question: str):

    history = get_history(session_id)

    # -------- GENERATE SEARCH QUERIES --------
    queries = rewrite_query(question, history)

    print("User question:", question)
    print("Search queries:", queries)

    all_results = []

    # -------- MULTI QUERY RETRIEVAL --------
    for q in queries:
        results = retrieve_chunks(q)
        all_results.extend(results)

    # -------- REMOVE DUPLICATES --------
    unique = {}

    for r in all_results:
        unique[r.id] = r

    results = list(unique.values())

    # -------- IF NO DOCUMENTS → NORMAL CHAT --------
    if not results:

        def chat_stream():

            answer = "I couldn't find information about that in the documents, but I'm happy to chat!"

            yield answer

            save_history(session_id, question, answer)

        return chat_stream()

    # -------- CONTEXT SELECTION --------
    context_chunks = []
    sources = set()

    for hit in results:

        score = getattr(hit, "score", 0.5)

        if score < SCORE_THRESHOLD:
            continue

        text = hit.payload["text"]
        source = hit.payload.get("source", "unknown")

        context_chunks.append(text)
        sources.add(source)

        if len(context_chunks) >= MAX_CONTEXT_CHUNKS:
            break

    if not context_chunks:

        def empty_stream():
            yield "I couldn't find relevant information in the documents."
        return empty_stream()

    # -------- FORMAT CONTEXT --------
    context_blocks = []

    for i, chunk in enumerate(context_chunks, start=1):
        context_blocks.append(
            f"""Document {i}
    ----------------
    {chunk}
    """
        )

    context = "\n\n".join(context_blocks)

    if len(context) > MAX_CONTEXT_LENGTH:
        context = context[:MAX_CONTEXT_LENGTH]

    # -------- LLM ANSWER --------
    def stream_response():

        full_answer = ""

        for token in generate_answer(context, question, history):
            full_answer += token
            yield token

        source_text = "\n\nSources:\n" + "\n".join([f"• {s}" for s in sources])

        yield source_text

        save_history(session_id, question, full_answer)

    return stream_response()

def delete_by_source(source: str):

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="source",
                    match=MatchValue(value=source)
                )
            ]
        )
    )

    return f"Deleted all chunks from source: {source}"


def list_documents():
    scroll_result = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=KEYWORD_SCROLL_LIMIT,
        with_payload=True,
        with_vectors=False,
    )

    points = scroll_result[0]

    docs = {}

    for point in points:
        source = point.payload.get("source", "unknown")
        category = point.payload.get("category", "unknown")

        if source not in docs:
            docs[source] = {
                "category": category,
                "chunks": 0
            }

        docs[source]["chunks"] += 1

    return docs


def delete_all_documents():

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter()
    )

    return "All documents deleted."