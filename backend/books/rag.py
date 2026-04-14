from __future__ import annotations

from typing import Any

import chromadb
import requests
from django.conf import settings
from sentence_transformers import SentenceTransformer

from .models import Book, BookChunk

_EMBEDDER: SentenceTransformer | None = None
_CHROMA = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
_COLLECTION = _CHROMA.get_or_create_collection("book_chunks")
LM_STUDIO_CHAT_URL = "http://localhost:1234/v1/chat/completions"
LM_STUDIO_MODEL = "local-model"


def _get_embedder() -> SentenceTransformer:
    global _EMBEDDER
    if _EMBEDDER is None:
        # Lazy load to avoid crashing Django startup when model download is unavailable.
        try:
            _EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError("Embedding model unavailable. Start internet/model cache and retry.") from exc
    return _EMBEDDER


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(end - overlap, start + 1)
    return chunks


def index_book(book: Book) -> None:
    content = f"{book.description}\n\n{book.summary}".strip()
    chunks = chunk_text(content)
    _COLLECTION.delete(where={"book_id": book.id})
    BookChunk.objects.filter(book=book).delete()

    if not chunks:
        return

    try:
        embeddings = _get_embedder().encode(chunks).tolist()
    except Exception:  # noqa: BLE001
        # Keep book saved even if vector indexing is temporarily unavailable.
        return
    ids = [f"book-{book.id}-chunk-{i}" for i in range(len(chunks))]
    metadatas = [{"book_id": book.id, "book_title": book.title, "chunk_index": i} for i in range(len(chunks))]

    _COLLECTION.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
    BookChunk.objects.bulk_create(
        [BookChunk(book=book, chunk_text=chunk, chunk_index=i) for i, chunk in enumerate(chunks)]
    )


def recommend_books(book_id: int, top_k: int = 3) -> list[Book]:
    book = Book.objects.filter(id=book_id).first()
    if not book:
        return []
    query_text = f"{book.title} {book.description} {book.genre}".strip()
    try:
        query_vector = _get_embedder().encode([query_text]).tolist()
        result = _COLLECTION.query(query_embeddings=query_vector, n_results=12, where={"book_id": {"$ne": book_id}})
    except Exception:  # noqa: BLE001
        return []
    ordered_ids: list[int] = []
    for metadata in (result.get("metadatas") or [[]])[0]:
        candidate_id = int(metadata["book_id"])
        if candidate_id != book_id and candidate_id not in ordered_ids:
            ordered_ids.append(candidate_id)
        if len(ordered_ids) >= top_k:
            break
    books_map = Book.objects.in_bulk(ordered_ids)
    return [books_map[book_pk] for book_pk in ordered_ids if book_pk in books_map]


def _llm_answer(prompt: str) -> str:
    try:
        response = requests.post(
            LM_STUDIO_CHAT_URL,
            json={
                "model": LM_STUDIO_MODEL,
                "temperature": 0.3,
                "messages": [
                    {
                        "role": "system",
                        "content": "Answer questions using only the provided context. Be accurate and concise.",
                    },
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=90,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
        return "I could not reach the local LLM at http://localhost:1234. Please start LM Studio and try again."


def ask_question(question: str, book_id: int | None = None) -> dict[str, Any]:
    try:
        query_vector = _get_embedder().encode([question]).tolist()
    except Exception:  # noqa: BLE001
        return {
            "answer": "Embeddings are unavailable right now. Ensure the sentence-transformers model is downloaded.",
            "sources": [],
        }
    where_clause = {"book_id": int(book_id)} if book_id else None
    result = _COLLECTION.query(query_embeddings=query_vector, n_results=5, where=where_clause)

    docs = (result.get("documents") or [[]])[0]
    metas = (result.get("metadatas") or [[]])[0]
    if not docs:
        return {"answer": "I could not find relevant context yet. Please upload books first.", "sources": []}

    context_lines = []
    source_titles: list[str] = []
    for document, metadata in zip(docs, metas):
        source_titles.append(metadata.get("book_title", "Unknown"))
        context_lines.append(f"[{metadata.get('book_title', 'Unknown')}] {document}")

    prompt = (
        f"Question: {question}\n\n"
        "Context:\n"
        + "\n\n".join(context_lines)
        + "\n\nProvide a direct answer and mention uncertainty when context is weak."
    )
    answer = _llm_answer(prompt)
    unique_sources = list(dict.fromkeys(source_titles))
    return {"answer": answer, "sources": unique_sources}
