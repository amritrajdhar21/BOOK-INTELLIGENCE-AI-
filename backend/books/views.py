from __future__ import annotations

import requests
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .ai_insights import classify_genre, generate_summary
from .models import Book, ChatHistory
from .rag import ask_question, index_book, recommend_books
from .serializers import BookDetailSerializer, BookListSerializer


@api_view(["GET"])
def books_list(request):
    books = Book.objects.order_by("-created_at")
    return Response(BookListSerializer(books, many=True).data)


@api_view(["GET"])
def book_detail(request, book_id: int):
    book = Book.objects.filter(id=book_id).first()
    if not book:
        return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(BookDetailSerializer(book).data)


@api_view(["GET"])
def book_recommendations(request, book_id: int):
    if not Book.objects.filter(id=book_id).exists():
        return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
    recs = recommend_books(book_id)
    return Response(BookListSerializer(recs, many=True).data)


def _fetch_book_from_url(book_url: str) -> dict:
    response = requests.get(book_url, timeout=30)
    response.raise_for_status()
    return {
        "title": book_url.split("/")[-2].replace("_", " ").title(),
        "author": "Unknown",
        "rating": 0,
        "description": response.text[:600],
        "cover_image_url": "",
        "book_url": book_url,
    }


@api_view(["POST"])
def upload_book(request):
    data = request.data
    book_payload = None

    if isinstance(data, dict) and data.get("book_url") and not data.get("title"):
        try:
            book_payload = _fetch_book_from_url(data["book_url"])
        except requests.RequestException as exc:
            return Response({"error": f"Failed to fetch book URL: {exc}"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        book_payload = data

    required = ["title", "book_url"]
    missing = [field for field in required if not book_payload.get(field)]
    if missing:
        return Response({"error": f"Missing required fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

    book, created = Book.objects.update_or_create(
        book_url=book_payload["book_url"],
        defaults={
            "title": book_payload.get("title", ""),
            "author": book_payload.get("author", "Unknown"),
            "rating": float(book_payload.get("rating", 0.0) or 0.0),
            "description": book_payload.get("description", ""),
            "cover_image_url": book_payload.get("cover_image_url", ""),
        },
    )

    try:
        book.summary = generate_summary(book.description, book.summary)
        book.genre = classify_genre(book.description, book.genre)
        book.save(update_fields=["summary", "genre"])
        index_book(book)
    except Exception as exc:  # noqa: BLE001
        return Response(
            {"error": f"Book saved but AI processing failed: {exc}", "book_id": book.id},
            status=status.HTTP_207_MULTI_STATUS,
        )

    code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return Response(BookDetailSerializer(book).data, status=code)


@api_view(["POST"])
def ask_book_question(request):
    question = request.data.get("question", "").strip()
    book_id = request.data.get("book_id")
    if not question:
        return Response({"error": "Question is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        rag_result = ask_question(question=question, book_id=book_id)
        ChatHistory.objects.create(
            question=question,
            answer=rag_result["answer"],
            sources=rag_result["sources"],
        )
        return Response(rag_result)
    except Exception as exc:  # noqa: BLE001
        return Response({"error": f"RAG pipeline failed: {exc}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
