from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [
    path("recipes/create", views.create_recipe, name="create_recipe"),
    path("recipes/list", login_required(views.RecipeListView.as_view()), name="list_recipes"),
    path("recipes/<int:recipe_id>/details", views.recipe_details, name="recipe_details"),
    path("recipes/<int:recipe_id>/delete", views.delete_recipe, name="delete_recipe"),
    path("recipes/<int:recipe_id>/edit", views.edit_recipe, name="edit_recipe"),
]