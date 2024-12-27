from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.forms import ModelForm
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.db import transaction

from .models import Recipe, RecipeIngredient, RecipeStep, RecipeTag
from . import forms
# import forms


class RecipeListView(ListView):
    paginate_by = 5
    model = Recipe

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user).order_by("name")


@login_required
def create_recipe(request):
    if request.method == "POST":
        context = {}
        recipe_form = forms.RecipeForm(request.POST)
        context["recipe_form"] = recipe_form
        is_error = False

        if not recipe_form.is_valid():
            context["info_error_message"] = "Помилка в інформації про рецепт"
            is_error = True

        steps = request.POST.getlist("step_description")
        for step in steps:
            if not forms.RecipeStepForm({"step_description": step}).is_valid():
                context["step_error_message"] = "Помилка в описі кроків рецепту"
                is_error = True
                break

        ingredients = list(zip(
            request.POST.getlist("ingredient_name"),
            request.POST.getlist("ingredient_volume"),
            request.POST.getlist("ingredient_volume_measure"),
        ))
        for name, volume, measure in ingredients:
            if not forms.RecipeIngredientForm({"name": name, "volume": volume, "volume_measure": measure}).is_valid():
                context["ingredient_error_message"] = "Помилка в описі інгредієнтів"
                is_error = True
                break

        tags = request.POST.getlist("tag_text")
        for tag in tags:
            if not forms.RecipeTagForm({"tag_text": tag}).is_valid():
                context["tag_error_message"] = "Помилка в заданні тегів"
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
        recipe_form = forms.RecipeForm()
        return render(request, "main/create_recipe.html", {"recipe_form": recipe_form})


@login_required
def recipe_details(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    # recipe = Recipe.objects.get(pk=recipe_id)

    if recipe.user != request.user:
        return render(request, "access_denied.html")

    ingredients = RecipeIngredient.objects.filter(recipe=recipe)
    steps = RecipeStep.objects.filter(recipe=recipe).order_by("step_number")
    tags = RecipeTag.objects.filter(recipe=recipe)
    # tags = RecipeTag.objects.filter(recipe_id=recipe_id)

    return render(
        request,
        "main/recipe_details.html",
        {"recipe": recipe, "ingredients": ingredients, "tags": tags, "steps": steps},
    )


@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    if recipe.user != request.user:
        return render(request, "access_denied.html")

    recipe_name = recipe.name

    if request.method == "POST":
        recipe.delete()
        return render(request, "main/delete_recipe_success.html", {"recipe_name": recipe_name})
    else:
        return render(request, "main/delete_recipe.html", {"recipe_name": recipe_name, "recipe_id": recipe.id})


def change_recipe_data_using_formset(formset, recipe):
    """Update or delete objects that corresponds to entries in formset"""
    for form in formset:
        obj = form.save(commit=False)
        obj.recipe = recipe
        # if data in a form marked for deletion
        if form.cleaned_data["DELETE"]:
            obj.delete()
        else:
            obj.save()


@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    if recipe.user != request.user:
        return render(request, "access_denied.html")

    if request.method == "POST":
        is_error = False
        recipe_form = forms.RecipeForm(request.POST, instance=recipe)
        step_formset = forms.RecipeStepFormSet(request.POST, instance=recipe)
        tag_formset = forms.RecipeTagFormSet(request.POST, instance=recipe)
        ingredient_formset = forms.RecipeIngredientFormSet(request.POST, instance=recipe)

        context = {
            "recipe_name": recipe.name,
            "recipe_form": recipe_form,
            "step_formset": step_formset,
            "tag_formset": tag_formset,
            "ingredient_formset": ingredient_formset,
        }

        # checking updated data for errors
        if not recipe_form.is_valid():
            context["info_error_message"] = "Помилка в інформації про рецепт"
            is_error = True
        if not step_formset.is_valid():
            context["step_error_message"] = "Помилка в описі кроків рецепту"
            is_error = True
        if not tag_formset.is_valid():
            print("\ntag_formset:")
            print(tag_formset._errors)
            context["tag_error_message"] = "Помилка в заданні тегів"
            is_error = True
        if not ingredient_formset.is_valid():
            print("\ningredient_formset:")
            print(ingredient_formset._errors)
            context["ingredient_error_message"] = "Помилка в описі інгредієнтів"
            is_error = True

        # checking new data for errors
        new_steps = request.POST.getlist("new_step_description")
        for step in new_steps:
            if not forms.RecipeStepForm({"step_description": step}).is_valid():
                context["step_error_message"] = "Помилка в описі кроків рецепту"
                is_error = True
                break

        new_ingredients = list(zip(
            request.POST.getlist("new_ingredient_name"),
            request.POST.getlist("new_ingredient_volume"),
            request.POST.getlist("new_ingredient_volume_measure"),
        ))
        for name, volume, measure in new_ingredients:
            if not forms.RecipeIngredientForm({"name": name, "volume": volume, "volume_measure": measure}).is_valid():
                context["ingredient_error_message"] = "Помилка в описі інгредієнтів"
                is_error = True
                break

        new_tags = request.POST.getlist("new_tag_text")
        for tag in new_tags:
            if not forms.RecipeTagForm({"tag_text": tag}).is_valid():
                context["tag_error_message"] = "Помилка в заданні тегів"
                is_error = True
                break

        if is_error:
            return render(request, "main/edit_recipe.html", context)
        else: # save data if no validation errors occured
            with transaction.atomic():
                # updated data
                recipe = recipe_form.save(commit=False)
                recipe.save()

                change_recipe_data_using_formset(step_formset, recipe)
                change_recipe_data_using_formset(tag_formset, recipe)
                change_recipe_data_using_formset(ingredient_formset, recipe)

                # new data
                start = RecipeStep.objects.aggregate(Max("step_number", default=0))["step_number__max"]
                for step_number, step in enumerate(new_steps, start):
                    RecipeStep.objects.create(recipe=recipe, step_number=step_number, step_description=step)

                for name, volume, measure in new_ingredients:
                    RecipeIngredient.objects.create(
                        recipe=recipe, name=name, volume=volume, volume_measure=measure
                    )

                for tag in new_tags:
                    RecipeTag.objects.create(recipe=recipe, tag_text=tag)

            return render(request, "main/edit_recipe_success.html")
    else:
        recipe_form = forms.RecipeForm(instance=recipe)
        step_formset = forms.RecipeStepFormSet(instance=recipe)
        tag_formset = forms.RecipeTagFormSet(instance=recipe)
        ingredient_formset = forms.RecipeIngredientFormSet(instance=recipe)

        return render(request, "main/edit_recipe.html", {
            "recipe_name": recipe.name,
            "recipe_form": recipe_form,
            "step_formset": step_formset,
            "tag_formset": tag_formset,
            "ingredient_formset": ingredient_formset,
        })
