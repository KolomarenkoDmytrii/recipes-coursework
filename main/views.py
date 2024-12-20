from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.forms import ModelForm
from django.contrib.auth.decorators import login_required

from .models import Recipe, RecipeIngredient, RecipeStep, RecipeTag

class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ["name", "description", "cooking_time", "category"]

        labels = {
            "name": "Назва страви",
            "description": "Опис",
            "cooking_time": "Час приготування",
            "category": "Категорія",
        }

@login_required
def create_recipe(request):
    if request.method == "POST":
        recipe_form = RecipeForm(request.POST)
        recipe = recipe_form.save(commit=False)
        recipe.user = request.user
        recipe.save()

        steps = request.POST.getlist("step_description")
        for step_number, step in enumerate(steps):
            RecipeStep.objects.create(recipe=recipe, step_number=step_number, step_description=step)

        ingredients = zip(
            request.POST.getlist("ingredient_name"),
            request.POST.getlist("ingredient_volume"),
            request.POST.getlist("ingredient_volume_measure"),
        )
        for name, volume, measure in ingredients:
            RecipeIngredient.objects.create(recipe=recipe, name=name, volume=volume, volume_measure=measure)

        tags = request.POST.getlist("tag_text")
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag_text=tag)

        # return redirect('recipe_detail', pk=recipe.pk)
        return redirect("home")
    else:
        recipe_form = RecipeForm()
        return render(request, "main/create_recipe.html", {"recipe_form": recipe_form})
        