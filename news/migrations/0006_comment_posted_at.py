# Generated by Django 4.2.2 on 2023-06-28 15:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0005_comment"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="posted_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
