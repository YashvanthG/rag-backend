import cohere

from app.core.config import settings
from app.core.qdrant_client import client
from app.core.constants import (
    COLLECTION_NAME,
    VECTOR_SEARCH_LIMIT,
    KEYWORD_SCROLL_LIMIT
)

from app.services.embedding_service import get_embedding


co = cohere.Client(settings.COHERE_API_KEY)


# ---------------------------
# Keyword Search
# ---------------------------

def keyword_search(query: str):

    scroll_result = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=KEYWORD_SCROLL_LIMIT,
        with_payload=True,
        with_vectors=False,
    )

    points = scroll_result[0]

    query_words = query.lower().split()

    results = []

    for p in points:
        text = p.payload.get("text", "").lower()

        for word in query_words:
            if word in text:
                results.append(p)
                break

    return results[:5]


# ---------------------------
# Cohere Rerank
# ---------------------------

def cohere_rerank(query: str, results):

    documents = [r.payload["text"] for r in results]

    response = co.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=documents,
        top_n=len(documents)
    )

    reranked = []

    for r in response.results:
        reranked.append(results[r.index])

    return reranked


# ---------------------------
# Local Rerank Fallback
# ---------------------------

def rerank_results(query: str, results):

    query_words = set(query.lower().split())

    scored = []

    for r in results:

        text = r.payload.get("text", "").lower()

        overlap = sum(1 for w in query_words if w in text)

        base_score = getattr(r, "score", 0.5)

        combined_score = base_score + overlap * 0.1

        scored.append((combined_score, r))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [r for _, r in scored]


# ---------------------------
# Retrieval Testing API
# ---------------------------

def test_retrieval(query: str):

    query_vector = get_embedding(query, "search_query")

    vector_results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=VECTOR_SEARCH_LIMIT,
    ).points

    keyword_results = keyword_search(query)

    results = []

    for r in vector_results:
        results.append({
            "id": r.id,
            "score": r.score,
            "type": "vector",
            "source": r.payload.get("source"),
            "text": r.payload.get("text")
        })

    for r in keyword_results:
        results.append({
            "id": r.id,
            "score": "keyword",
            "type": "keyword",
            "source": r.payload.get("source"),
            "text": r.payload.get("text")
        })

    unique = {}

    for r in results:
        unique[r["id"]] = r

    results = list(unique.values())

    results = sorted(
        results,
        key=lambda x: 0 if x["score"] == "keyword" else x["score"],
        reverse=True
    )

    output = []

    for r in results[:5]:

        output.append({
            "score": r["score"],
            "type": r["type"],
            "source": r["source"],
            "text": r["text"][:200]
        })

    return output


# ---------------------------
# Main Retrieval Function
# ---------------------------

def retrieve_chunks(query: str):

    query_vector = get_embedding(query, "search_query")

    vector_results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=VECTOR_SEARCH_LIMIT,
    ).points

    keyword_results = keyword_search(query)

    results = vector_results + keyword_results

    unique = {}

    for r in results:
        unique[r.id] = r

    results = list(unique.values())

    try:
        results = cohere_rerank(query, results)
    except Exception:
        results = rerank_results(query, results)

    return results