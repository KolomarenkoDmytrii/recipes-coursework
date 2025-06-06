# Generated by Django 5.1.4 on 2024-12-29 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0003_alter_recipe_image_alter_recipestep_image"),
    ]

    operations = [
        migrations.RenameField(
            model_name="recipe",
            old_name="image",
            new_name="image_1",
        ),
        migrations.RemoveField(
            model_name="recipestep",
            name="image",
        ),
        migrations.AddField(
            model_name="recipe",
            name="image_2",
            field=models.ImageField(blank=True, default="", upload_to="recipes"),
        ),
        migrations.AddField(
            model_name="recipe",
            name="image_3",
            field=models.ImageField(blank=True, default="", upload_to="recipes"),
        ),
    ]
