# Generated by Django 4.2.5 on 2023-09-23 20:33

import django.db.models.deletion
import files.utils
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="File",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(blank=True, null=True, upload_to=files.utils.get_upload_path)),
                ("original_file_name", models.TextField()),
                ("file_name", models.CharField(max_length=255, unique=True)),
                ("file_type", models.CharField(max_length=255)),
                ("uploaded_at", models.DateTimeField(blank=True, null=True)),
                (
                    "uploader",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
    ]