# Generated by Django 4.2.16 on 2024-09-23 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questions", "0016_remove_questionlocale_products"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="update_topic_counter",
            field=models.IntegerField(default=0),
        ),
    ]
