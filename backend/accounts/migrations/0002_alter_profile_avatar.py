# Generated by Django 4.2.2 on 2023-07-01 15:26

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="avatar",
            field=models.ImageField(null=True, upload_to=accounts.models.get_image_filename),
        ),
    ]
