from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("author", models.CharField(default="Unknown", max_length=255)),
                ("rating", models.FloatField(default=0.0)),
                ("description", models.TextField(blank=True, default="")),
                ("genre", models.CharField(blank=True, default="", max_length=100)),
                ("summary", models.TextField(blank=True, default="")),
                ("book_url", models.URLField(unique=True)),
                ("cover_image_url", models.URLField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="ChatHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question", models.TextField()),
                ("answer", models.TextField()),
                ("sources", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="BookChunk",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("chunk_text", models.TextField()),
                ("chunk_index", models.PositiveIntegerField()),
                (
                    "book",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chunks", to="books.book"),
                ),
            ],
            options={"ordering": ["chunk_index"], "unique_together": {("book", "chunk_index")}},
        ),
    ]
