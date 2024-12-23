from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.forms import ModelForm
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required

from .models import Recipe, RecipeIngredient, RecipeStep, RecipeTag


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ["name", "description", "cooking_time", "category"]

        labels = {
            "name": "Назва страви",
            "description": "Опис",
            "cooking_time": "Час приготування, хв",
            "category": "Категорія",
        }


class RecipeIngredientForm(ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["name", "volume", "volume_measure"]


class RecipeStepForm(ModelForm):
    class Meta:
        model = RecipeStep
        fields = ["step_description"]


class RecipeTagForm(ModelForm):
    class Meta:
        model = RecipeTag
        fields = ["tag_text"]


class RecipeListView(ListView):
    paginate_by = 5
    model = Recipe

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user).order_by("name")


@login_required
def create_recipe(request):
    if request.method == "POST":
        context = {}
        recipe_form = RecipeForm(request.POST)
        context["recipe_form"] = recipe_form
        is_error = False

        if not recipe_form.is_valid():
            context["info_error_message"] = "Помилка в інформації про рецепт"
            is_error = True

        steps = request.POST.getlist("step_description")
        for step in steps:
            if not RecipeStepForm({"step_description": step}).is_valid():
                context["step_error_message"] = "Помилка в описі кроків рецепту"
                is_error = True
                break

        ingredients = zip(
            request.POST.getlist("ingredient_name"),
            request.POST.getlist("ingredient_volume"),
            request.POST.getlist("ingredient_volume_measure"),
        )
        for name, volume, measure in ingredients:
            if not RecipeIngredientForm({"name": name, "volume": volume, "volume_measure": measure}).is_valid():
                context["ingredient_error_message"] = "Помилка в описі інгредієнта"
                is_error = True
                break

        tags = request.POST.getlist("tag_text")
        for tag in tags:
            if not RecipeIngredientForm({"tag_text": tag}).is_valid():
                context["tag_error_message"] = "Помилка в заданні тегу"
                is_error = True
                break

        if is_error:
            print(context)
            return render(request, "main/create_recipe.html", context)
        else: # save data if no validation errors occured
            recipe = recipe_form.save(commit=False)
            recipe.user = request.user
            recipe.save()

            for step_number, step in enumerate(steps):
                RecipeStep.objects.create(recipe=recipe, step_number=step_number, step_description=step)

            for name, volume, measure in ingredients:
                RecipeIngredient.objects.create(
                    recipe=recipe, name=name, volume=volume, volume_measure=measure
                )

            for tag in tags:
                RecipeTag.objects.create(recipe=recipe, tag_text=tag)

            return render(request, "main/create_recipe_success.html")
    else:
        recipe_form = RecipeForm()
        return render(request, "main/create_recipe.html", {"recipe_form": recipe_form})


@login_required
def recipe_details(request, recipe_id):
    recipe = Recipe.objects.get(pk=recipe_id)

    if recipe.user != request.user:
        return render(request, "access_denied.html")

    ingredients = RecipeIngredient.objects.filter(recipe_id=recipe_id)
    steps = RecipeStep.objects.filter(recipe_id=recipe_id).order_by("step_number")
    tags = RecipeTag.objects.filter(recipe_id=recipe_id)

    return render(
        request,
        "main/recipe_details.html",
        {"recipe": recipe, "ingredients": ingredients, "tags": tags, "steps": steps},
    )


@login_required
def delete_recipe(request, recipe_id):
    recipe = Recipe.objects.get(pk=recipe_id)

    if recipe.user != request.user:
        return render(request, "access_denied.html")

    recipe_name = recipe.name

    if request.method == "POST":
        recipe.delete()
        return render(request, "main/delete_recipe_success.html", {"recipe_name": recipe_name})
    else:
        return render(request, "main/delete_recipe.html", {"recipe_name": recipe_name, "recipe_id": recipe.id})
