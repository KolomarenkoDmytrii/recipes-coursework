from django.urls import path

from . import views


urlpatterns = [
    path("recipes/create", views.create_recipe, name="create_recipe"),
    path("recipes/list", views.list_recipes, name="list_recipes"),
    path("recipes/search_menu", views.search_menu, name="search_menu"),
    path("recipes/search", views.search_results, name="search_results"),
    path("recipes/generate", views.generate_recipe, name="generate_recipe"),
    path(
        "recipes/<int:recipe_id>/details", views.recipe_details, name="recipe_details"
    ),
    path("recipes/<int:recipe_id>/delete", views.delete_recipe, name="delete_recipe"),
    path("recipes/<int:recipe_id>/edit", views.edit_recipe, name="edit_recipe"),
]
