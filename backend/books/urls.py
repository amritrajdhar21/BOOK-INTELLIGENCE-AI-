from django.urls import path

from .views import ask_book_question, book_detail, book_recommendations, books_list, upload_book

urlpatterns = [
    path("books/", books_list, name="books-list"),
    path("books/<int:book_id>/", book_detail, name="book-detail"),
    path("books/<int:book_id>/recommendations/", book_recommendations, name="book-recommendations"),
    path("books/upload/", upload_book, name="book-upload"),
    path("books/ask/", ask_book_question, name="book-ask"),
]
