import cohere
from app.core.config import settings

co = cohere.Client(settings.COHERE_API_KEY)


# -------- SINGLE EMBEDDING (for queries) --------
def get_embedding(text: str, input_type="search_query"):

    response = co.embed(
        texts=[text],
        model="embed-english-v3.0",
        input_type=input_type
    )

    return response.embeddings[0]


# -------- BATCH EMBEDDINGS (for documents) --------
def get_embeddings(texts, input_type="search_document"):

    response = co.embed(
        texts=texts,
        model="embed-english-v3.0",
        input_type=input_type
    )

    return response.embeddings