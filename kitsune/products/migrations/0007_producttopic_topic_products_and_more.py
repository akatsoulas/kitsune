# Generated by Django 4.2.11 on 2024-06-10 05:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0006_alter_product_and_topic_images"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductTopic",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="products.product"
                    ),
                ),
                (
                    "topic",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="products.topic"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="topic",
            name="products",
            field=models.ManyToManyField(
                related_name="m2m_topics", through="products.ProductTopic", to="products.product"
            ),
        ),
        migrations.AddConstraint(
            model_name="producttopic",
            constraint=models.UniqueConstraint(
                fields=("product", "topic"), name="unique_product_topic"
            ),
        ),
    ]
