# Generated by Django 5.0 on 2023-12-24 12:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("emails", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="domaininfo",
            name="country_code",
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name="emailinfo",
            name="country_code",
            field=models.CharField(max_length=2, null=True),
        ),
    ]
