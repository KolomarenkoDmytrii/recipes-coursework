from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.forms import ModelForm
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required

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
                context["ingredient_error_message"] = "Помилка в описі інгредієнта"
                is_error = True
                break

        tags = request.POST.getlist("tag_text")
        for tag in tags:
            if not forms.RecipeTagForm({"tag_text": tag}).is_valid():
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
    # recipe = Recipe.objects.get(pk=recipe_id)

    if recipe.user != request.user:
        return render(request, "access_denied.html")

    recipe_name = recipe.name

    if request.method == "POST":
        recipe.delete()
        return render(request, "main/delete_recipe_success.html", {"recipe_name": recipe_name})
    else:
        return render(request, "main/delete_recipe.html", {"recipe_name": recipe_name, "recipe_id": recipe.id})


# @login_required
# def edit_recipe(request, recipe_id):
#     recipe = get_object_or_404(Recipe, pk=recipe_id)

#     if recipe.user != request.user:
#         return render(request, "access_denied.html")

#     recipe_form = forms.RecipeForm(instance=recipe)
#     step_formset = forms.RecipeStepFormSet(queryset=RecipeStep.objects.filter(recipe=recipe))
#     tag_formset = forms.RecipeTagFormSet(queryset=RecipeTag.objects.filter(recipe=recipe))
#     ingredient_formset = forms.RecipeIngredientFormSet(queryset=RecipeIngredient.objects.filter(recipe=recipe))

#     if request.method == "POST":
#         recipe_form = forms.RecipeForm(request.POST, instance=recipe)
#         step_formset = forms.RecipeStepFormSet(request.POST)
#         tag_formset = forms.RecipeTagFormSet(request.POST)
#         ingredient_formset = forms.RecipeIngredientFormSet(request.POST)

#         if recipe_form.is_valid() and step_formset.is_valid() and tag_formset.is_valid() and ingredient_formset.is_valid():
#             # Збереження рецепту
#             recipe_form.save()

#             # Збереження кроків
#             for form in step_formset:
#                 step = form.save(commit=False)
#                 step.recipe = recipe
#                 step.save()

#             # Збереження тегів
#             for form in tag_formset:
#                 tag = form.save(commit=False)
#                 tag.recipe = recipe
#                 tag.save()

#             # Збереження інгредієнтів
#             for form in ingredient_formset:
#                 ingredient = form.save(commit=False)
#                 ingredient.recipe = recipe
#                 ingredient.save()

#             return redirect("list_recipes")

#     return render(request, "main/edit_recipe.html", {
#         "recipe_form": recipe_form,
#         "step_formset": step_formset,
#         "tag_formset": tag_formset,
#         "ingredient_formset": ingredient_formset,
#         "recipe": recipe
#     })
@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    if recipe.user != request.user:
        return render(request, "access_denied.html")

    ingredients = RecipeIngredient.objects.filter(recipe=recipe)
    steps = RecipeStep.objects.filter(recipe=recipe).order_by("step_number")
    tags = RecipeTag.objects.filter(recipe=recipe)
    
    context = {}
    context["ingredients"] = ingredients
    context["steps"] = steps
    context["tags"] = tags

    if request.method == "POST":
        recipe_form = forms.RecipeForm(request.POST, instance=recipe)
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
                context["ingredient_error_message"] = "Помилка в описі інгредієнта"
                is_error = True
                break

        tags = request.POST.getlist("tag_text")
        for tag in tags:
            if not forms.RecipeTagForm({"tag_text": tag}).is_valid():
                context["tag_error_message"] = "Помилка в заданні тегу"
                is_error = True
                break

        if is_error:
            print(context)
            return render(request, "main/create_recipe.html", context)
        else: # save data if no validation errors occured
            recipe = recipe_form.save(commit=False)
            recipe.save()

            RecipeStep.objects.filter(recipe=recipe).delete()
            RecipeIngredient.objects.filter(recipe=recipe).delete()
            RecipeTag.objects.filter(recipe=recipe).delete()

            for step_number, step in enumerate(steps):
                RecipeStep.objects.create(recipe=recipe, step_number=step_number, step_description=step)

            for name, volume, measure in ingredients:
                RecipeIngredient.objects.create(
                    recipe=recipe, name=name, volume=volume, volume_measure=measure
                )

            for tag in tags:
                RecipeTag.objects.create(recipe=recipe, tag_text=tag)

            return render(request, "main/edit_recipe_success.html")
    else:
        context["recipe_form"] = forms.RecipeForm(instance=recipe)

        return render(request, "main/edit_recipe.html", context)
