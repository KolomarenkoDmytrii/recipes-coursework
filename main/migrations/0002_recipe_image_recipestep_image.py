# Generated by Django 5.1.4 on 2024-12-28 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="image",
            field=models.ImageField(null=True, upload_to="recipes"),
        ),
        migrations.AddField(
            model_name="recipestep",
            name="image",
            field=models.ImageField(null=True, upload_to="recipes"),
        ),
    ]
