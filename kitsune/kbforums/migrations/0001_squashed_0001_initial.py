# Generated by Django 4.1.9 on 2023-06-14 08:13

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    replaces = [("kbforums", "0001_initial")]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("wiki", "0001_squashed_0013_alter_document_related_documents_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("content", models.TextField()),
                ("created", models.DateTimeField(db_index=True, default=datetime.datetime.now)),
                ("updated", models.DateTimeField(db_index=True, default=datetime.datetime.now)),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="wiki_post_set",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["created"],
            },
        ),
        migrations.CreateModel(
            name="Thread",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("created", models.DateTimeField(db_index=True, default=datetime.datetime.now)),
                ("replies", models.IntegerField(default=0)),
                ("is_locked", models.BooleanField(default=False)),
                ("is_sticky", models.BooleanField(db_index=True, default=False)),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="wiki_thread_set",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="wiki.document"
                    ),
                ),
                (
                    "last_post",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="last_post_in",
                        to="kbforums.post",
                    ),
                ),
            ],
            options={
                "ordering": ["-is_sticky", "-last_post__created"],
                "permissions": (
                    ("lock_thread", "Can lock KB threads"),
                    ("sticky_thread", "Can sticky KB threads"),
                ),
            },
        ),
        migrations.AddField(
            model_name="post",
            name="thread",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="kbforums.thread"
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="updated_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="wiki_post_last_updated_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
