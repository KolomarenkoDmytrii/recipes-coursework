from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q
from django.db import transaction
from django.http import HttpResponseRedirect

from .models import Recipe, RecipeIngredient, RecipeStep, RecipeTag
from .ai import get_generated_recipe
from . import forms


class RecipeListView(ListView):
    paginate_by = 5
    model = Recipe
    template_name = "main/recipe_list.html"

    def get_queryset(self):
        sort_by = (
            "-" if self.request.GET.get("is_descending", False) else ""
        ) + self.request.GET.get("ordering", "name")

        return Recipe.objects.filter(user=self.request.user).order_by(sort_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sort_form"] = forms.SortRecipeListForm(
            initial={
                "ordering": self.request.GET.get("ordering", "name"),
                "is_descending": self.request.GET.get("is_descending", False),
            }
        )
        return context


list_recipes = login_required(RecipeListView.as_view())


class SearchResultsView(ListView):
    model = Recipe
    template_name = "main/search_results.html"
    context_object_name = "recipes"
    paginate_by = 5

    def get_queryset(self):
        query = forms.SearchForm(self.request.GET)

        if query.is_valid():
            search_string = query.cleaned_data["search_string"]

            recipe_search_params = []
            if query.cleaned_data["search_in_names"]:
                recipe_search_params.append(Q(name__icontains=search_string))
            if query.cleaned_data["search_in_descriptions"]:
                recipe_search_params.append(Q(description__icontains=search_string))
            if query.cleaned_data["search_in_categories"]:
                recipe_search_params.append(Q(category__icontains=search_string))
            if query.cleaned_data["search_in_ingredients"]:
                recipe_search_params.append(
                    Q(recipeingredient__name__icontains=search_string)
                )
            if query.cleaned_data["search_in_tags"]:
                recipe_search_params.append(
                    Q(recipetag__tag_text__icontains=search_string)
                )

            if len(recipe_search_params) != 0:
                recipe_search_params_combined = recipe_search_params[0]
                for param in recipe_search_params[1:]:
                    recipe_search_params_combined = (
                        recipe_search_params_combined | param
                    )

                return Recipe.objects.filter(
                    recipe_search_params_combined, user=self.request.user
                ).order_by("name")

            return Recipe.objects.none()
        else:
            return Recipe.objects.none()


search_results = login_required(SearchResultsView.as_view())


@login_required
def search_menu(request):
    return render(request, "main/search_menu.html", {"search_form": forms.SearchForm()})


@login_required
def create_recipe(request):
    if request.method == "POST":
        context = {}
        recipe_form = forms.RecipeForm(request.POST, request.FILES)
        context["recipe_form"] = recipe_form
        is_error = False

        ingredients = list(
            zip(
                request.POST.getlist("new_ingredient_name"),
                request.POST.getlist("new_ingredient_volume"),
                request.POST.getlist("new_ingredient_volume_measure"),
            )
        )
        steps = request.POST.getlist("new_step_description")
        tags = request.POST.getlist("new_tag_text")

        context["new_ingredients"] = [
            {"name": name, "volume": volume, "volume_measure": measure}
            for name, volume, measure in ingredients
        ]
        context["new_steps"] = steps
        context["new_tags"] = tags

        if not recipe_form.is_valid():
            context["info_error_message"] = "Помилка в інформації про рецепт"
            is_error = True

        for step in steps:
            if not forms.RecipeStepForm({"step_description": step}).is_valid():
                context["step_error_message"] = "Помилка в описі кроків рецепту"
                is_error = True
                break

        for name, volume, measure in ingredients:
            if not forms.RecipeIngredientForm(
                {"name": name, "volume": volume, "volume_measure": measure}
            ).is_valid():
                context["ingredient_error_message"] = "Помилка в описі інгредієнтів"
                is_error = True
                break

        for tag in tags:
            if not forms.RecipeTagForm({"tag_text": tag}).is_valid():
                context["tag_error_message"] = "Помилка в заданні тегів"
                is_error = True
                break

        if is_error:
            return render(request, "main/create_recipe.html", context)

        # save data if no validation errors occured
        with transaction.atomic():
            recipe = recipe_form.save(commit=False)
            recipe.user = request.user
            recipe.save()

            for step_number, step in enumerate(steps):
                RecipeStep.objects.create(
                    recipe=recipe, step_number=step_number, step_description=step
                )

            for name, volume, measure in ingredients:
                RecipeIngredient.objects.create(
                    recipe=recipe, name=name, volume=volume, volume_measure=measure
                )

            for tag in tags:
                RecipeTag.objects.create(recipe=recipe, tag_text=tag)

        return render(request, "main/create_recipe_success.html", {"recipe_id": recipe.id})
    else:
        recipe_form = forms.RecipeForm()
        return render(request, "main/create_recipe.html", {"recipe_form": recipe_form})


@login_required
def recipe_details(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    if recipe.user != request.user:
        return render(request, "access_denied.html")

    ingredients = RecipeIngredient.objects.filter(recipe=recipe)
    steps = RecipeStep.objects.filter(recipe=recipe).order_by("step_number")
    tags = RecipeTag.objects.filter(recipe=recipe)

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
        return render(
            request, "main/delete_recipe_success.html", {"recipe_name": recipe_name}
        )

    return render(
        request,
        "main/delete_recipe.html",
        {"recipe_name": recipe_name, "recipe_id": recipe.id},
    )


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
        recipe_form = forms.RecipeForm(request.POST, request.FILES, instance=recipe)
        step_formset = forms.RecipeStepFormSet(request.POST, instance=recipe)
        tag_formset = forms.RecipeTagFormSet(request.POST, instance=recipe)
        ingredient_formset = forms.RecipeIngredientFormSet(
            request.POST, instance=recipe
        )

        context = {
            "recipe_name": recipe.name,
            "recipe_form": recipe_form,
            "step_formset": step_formset,
            "tag_formset": tag_formset,
            "ingredient_formset": ingredient_formset,
        }

        new_ingredients = list(
            zip(
                request.POST.getlist("new_ingredient_name"),
                request.POST.getlist("new_ingredient_volume"),
                request.POST.getlist("new_ingredient_volume_measure"),
            )
        )
        new_steps = request.POST.getlist("new_step_description")
        new_tags = request.POST.getlist("new_tag_text")

        context["new_ingredients"] = [
            {"name": name, "volume": volume, "volume_measure": measure}
            for name, volume, measure in new_ingredients
        ]
        context["new_steps"] = new_steps
        context["new_tags"] = new_tags

        # checking updated data for errors
        if not recipe_form.is_valid():
            context["info_error_message"] = "Помилка в інформації про рецепт"
            is_error = True
        if not step_formset.is_valid():
            context["step_error_message"] = "Помилка в описі кроків рецепту"
            is_error = True
        if not tag_formset.is_valid():
            context["tag_error_message"] = "Помилка в заданні тегів"
            is_error = True
        if not ingredient_formset.is_valid():
            context["ingredient_error_message"] = "Помилка в описі інгредієнтів"
            is_error = True

        # checking new data for errors
        for step in new_steps:
            if not forms.RecipeStepForm({"step_description": step}).is_valid():
                context["step_error_message"] = "Помилка в описі кроків рецепту"
                is_error = True
                break

        for name, volume, measure in new_ingredients:
            if not forms.RecipeIngredientForm(
                {"name": name, "volume": volume, "volume_measure": measure}
            ).is_valid():
                context["ingredient_error_message"] = "Помилка в описі інгредієнтів"
                is_error = True
                break

        for tag in new_tags:
            if not forms.RecipeTagForm({"tag_text": tag}).is_valid():
                context["tag_error_message"] = "Помилка в заданні тегів"
                is_error = True
                break

        if is_error:
            return render(request, "main/edit_recipe.html", context)

        # save data if no validation errors occured
        with transaction.atomic():
            # updated data
            recipe = recipe_form.save(commit=False)
            recipe.save()

            change_recipe_data_using_formset(step_formset, recipe)
            change_recipe_data_using_formset(tag_formset, recipe)
            change_recipe_data_using_formset(ingredient_formset, recipe)

            # new data
            start = RecipeStep.objects.aggregate(Max("step_number", default=0))[
                "step_number__max"
            ]
            for step_number, step in enumerate(new_steps, start):
                RecipeStep.objects.create(
                    recipe=recipe, step_number=step_number, step_description=step
                )

            for name, volume, measure in new_ingredients:
                RecipeIngredient.objects.create(
                    recipe=recipe, name=name, volume=volume, volume_measure=measure
                )

            for tag in new_tags:
                RecipeTag.objects.create(recipe=recipe, tag_text=tag)

        return render(request, "main/edit_recipe_success.html", {"recipe_id": recipe.id})
    else:
        recipe_form = forms.RecipeForm(instance=recipe)
        step_formset = forms.RecipeStepFormSet(instance=recipe)
        tag_formset = forms.RecipeTagFormSet(instance=recipe)
        ingredient_formset = forms.RecipeIngredientFormSet(instance=recipe)

        return render(
            request,
            "main/edit_recipe.html",
            {
                "recipe_name": recipe.name,
                "recipe_form": recipe_form,
                "step_formset": step_formset,
                "tag_formset": tag_formset,
                "ingredient_formset": ingredient_formset,
            },
        )


@login_required
def generate_recipe(request):
    if request.method == "POST":
        form = forms.RecipeGenerationForm(request.POST)
        if form.is_valid():
            recipe_data = get_generated_recipe(
                form.cleaned_data["ingredients_description"],
                form.cleaned_data["recipe_description"],
            )

            recipe_info_form = forms.RecipeForm(
                {
                    "name": recipe_data["name"],
                    "description": recipe_data["description"],
                    "cooking_time": recipe_data["cooking_time_in_minutes"],
                    "category": recipe_data["category"],
                }
            )

            return render(
                request,
                "main/generating_recipe_result.html",
                {
                    "recipe": recipe_data,
                    "recipe_info_form": recipe_info_form,
                    "generation_input_form": form,
                },
            )

        return render(
            request,
            "main/generating_recipe_input.html",
            {"input_form": form},
        )

    return render(
        request,
        "main/generating_recipe_input.html",
        {"input_form": forms.RecipeGenerationForm()},
    )
