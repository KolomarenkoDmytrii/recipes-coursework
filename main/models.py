import os
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver


def get_recipe_image_path(instance, filename):
    return f"recipes/{str(uuid.uuid4())}_{filename}"


# Create your models here.
class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.TextField()
    # in minutes
    cooking_time = models.PositiveIntegerField()
    category = models.CharField(max_length=128)
    image_1 = models.ImageField(upload_to=get_recipe_image_path, blank=True, default="")
    image_2 = models.ImageField(upload_to=get_recipe_image_path, blank=True, default="")
    image_3 = models.ImageField(upload_to=get_recipe_image_path, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RecipeStep(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField()
    step_description = models.CharField(max_length=512)

    class Meta:
        unique_together = ["recipe", "step_number"]
        ordering = ["step_number"]


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag_text = models.CharField(max_length=80)

    class Meta:
        unique_together = ["recipe", "tag_text"]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    volume = models.FloatField()
    volume_measure = models.CharField(max_length=12)


@receiver(models.signals.post_delete, sender=Recipe)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes images from filesystem
    when corresponding Recipe object is deleted.
    """
    if instance.image_1:
        if os.path.isfile(instance.image_1.path):
            os.remove(instance.image_1.path)

    if instance.image_2:
        if os.path.isfile(instance.image_2.path):
            os.remove(instance.image_2.path)

    if instance.image_3:
        if os.path.isfile(instance.image_3.path):
            os.remove(instance.image_3.path)


@receiver(models.signals.pre_save, sender=Recipe)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old images from filesystem
    when corresponding Recipe object is updated
    with new images.
    """
    if not instance.pk:
        return False

    try:
        old_obj = sender.objects.get(pk=instance.pk)
        old_image_1 = old_obj.image_1
        old_image_2 = old_obj.image_2
        old_image_3 = old_obj.image_3

        new_image_1 = instance.image_1
        new_image_2 = instance.image_2
        new_image_3 = instance.image_3

        if not old_image_1 == new_image_1:
            if old_image_1 and os.path.isfile(old_image_1.path):
                os.remove(old_image_1.path)

        if not old_image_2 == new_image_2:
            if old_image_2 and os.path.isfile(old_image_2.path):
                os.remove(old_image_2.path)

        if not old_image_3 == new_image_3:
            if old_image_3 and os.path.isfile(old_image_3.path):
                os.remove(old_image_3.path)
    except sender.DoesNotExist:
        return False
