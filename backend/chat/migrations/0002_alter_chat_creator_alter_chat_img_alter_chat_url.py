# Generated by Django 4.2.3 on 2023-08-02 20:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("chat", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chat",
            name="creator",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name="chat",
            name="img",
            field=models.ImageField(blank=True, default="default-user-avatar.jpg", null=True, upload_to="chat_img"),
        ),
        migrations.AlterField(
            model_name="chat",
            name="url",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
