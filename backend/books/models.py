from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, default="Unknown")
    rating = models.FloatField(default=0.0)
    description = models.TextField(blank=True, default="")
    genre = models.CharField(max_length=100, blank=True, default="")
    summary = models.TextField(blank=True, default="")
    book_url = models.URLField(unique=True)
    cover_image_url = models.URLField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class BookChunk(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="chunks")
    chunk_text = models.TextField()
    chunk_index = models.PositiveIntegerField()

    class Meta:
        unique_together = ("book", "chunk_index")
        ordering = ["chunk_index"]


class ChatHistory(models.Model):
    question = models.TextField()
    answer = models.TextField()
    sources = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
