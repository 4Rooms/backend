# Generated by Django 4.2.5 on 2023-10-19 20:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0011_alter_message_text"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chat",
            name="img",
            field=models.ImageField(blank=True, null=True, upload_to="chat_img"),
        ),
    ]
