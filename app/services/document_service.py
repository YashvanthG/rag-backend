import uuid
from nltk.tokenize import sent_tokenize

from app.services.embedding_service import get_embeddings
from app.core.qdrant_client import client
from app.core.constants import COLLECTION_NAME


def chunk_text(
    text: str,
    max_chunk_size: int = 900,
    overlap_sentences: int = 2
):
    """
    Semantic chunking using sentences with overlap.
    """

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        sentences = sent_tokenize(paragraph)

        current_chunk = []
        current_length = 0

        for sentence in sentences:

            sentence_length = len(sentence)

            if current_length + sentence_length <= max_chunk_size:

                current_chunk.append(sentence)
                current_length += sentence_length

            else:

                chunks.append(" ".join(current_chunk))

                # overlap sentences
                overlap = (
                    current_chunk[-overlap_sentences:]
                    if overlap_sentences <= len(current_chunk)
                    else current_chunk
                )

                current_chunk = overlap + [sentence]
                current_length = sum(len(s) for s in current_chunk)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

    return chunks


def upload_text(
    text: str,
    source: str = "manual",
    category: str = "general"
):

    chunks = chunk_text(text)

    if not chunks:
        return "No content found."

    # -------- BATCH EMBEDDINGS --------
    embeddings = get_embeddings(chunks, "search_document")

    points = []

    for chunk, embedding in zip(chunks, embeddings):

        points.append({
            "id": str(uuid.uuid4()),
            "vector": embedding,
            "payload": {
                "text": chunk,
                "source": source,
                "category": category
            }
        })

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    return f"Stored {len(points)} chunks successfully!"