from django.urls import path

from . import views


urlpatterns = [
    path("create", views.create_recipe, name="create_recipe"),
    path("list", views.list_recipes, name="list_recipes"),
    path("search_menu", views.search_menu, name="search_menu"),
    path("search", views.search_results, name="search_results"),
    path("generate", views.generate_recipe, name="generate_recipe"),
    path("<int:recipe_id>/details", views.recipe_details, name="recipe_details"),
    path("<int:recipe_id>/delete", views.delete_recipe, name="delete_recipe"),
    path("<int:recipe_id>/edit", views.edit_recipe, name="edit_recipe"),
    path("<int:recipe_id>/text-download", views.download_recipe, name="download_recipe"),
]
