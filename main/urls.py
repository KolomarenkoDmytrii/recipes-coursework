from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [
    # path("", views.index, name="index"),
    path("recipes/create", views.create_recipe, name="create_recipe"),
    path("recipes/list", login_required(views.RecipeListView.as_view()), name="list_recipes"),
    path("recipes/details/<int:recipe_id>", views.recipe_details, name="recipe_details"),
]