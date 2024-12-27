from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.TextField()
    # in minutes
    cooking_time = models.PositiveIntegerField()
    category = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RecipeStep(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField()
    step_description = models.CharField(max_length=512)


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag_text = models.CharField(max_length=80)

    class Meta:
        unique_together = ("recipe", "tag_text")


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    volume = models.FloatField()
    volume_measure = models.CharField(max_length=12)
