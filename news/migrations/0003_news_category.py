# Generated by Django 4.2.2 on 2023-06-27 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0002_news"),
    ]

    operations = [
        migrations.AddField(
            model_name="news",
            name="category",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="news.category",
            ),
            preserve_default=False,
        ),
    ]
