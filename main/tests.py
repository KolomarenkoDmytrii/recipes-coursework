import datetime

from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth.models import User
from .models import Recipe, RecipeIngredient, RecipeStep, RecipeTag


class ListRecipesViewTest(TestCase):
    sorting_params = ["name", "cooking_time", "category", "created_at", "updated_at"]

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="user", password="123456")

        cls.recipes = [
            Recipe.objects.create(
                user=cls.user,
                name="test 1",
                description="test",
                cooking_time=30,
                category="test a",
                created_at=datetime.datetime(2025, 1, 13, 14, 30),
                updated_at=datetime.datetime(2025, 1, 13, 15, 30),
            ),
            Recipe.objects.create(
                user=cls.user,
                name="test 2",
                description="test",
                cooking_time=20,
                category="test c",
                created_at=datetime.datetime(2025, 1, 12, 14, 30),
                updated_at=datetime.datetime(2025, 1, 13, 15, 10),
            ),
            Recipe.objects.create(
                user=cls.user,
                name="test 3",
                description="test",
                cooking_time=10,
                category="test b",
                created_at=datetime.datetime(2025, 1, 11, 14, 30),
                updated_at=datetime.datetime(2025, 1, 13, 14, 40),
            ),
        ]

    def setUp(self):
        self.client.login(username="user", password="123456")

    def test_sorting(self):
        for sorting_param in self.sorting_params:
            with self.subTest(
                msg=f"Test sorting by {sorting_param}", sorting_param=sorting_param
            ):
                response = self.client.get(
                    reverse("list_recipes"), data={"ordering": sorting_param}
                )
                self.assertEqual(
                    list(response.context["object_list"]),
                    sorted(self.recipes, key=lambda r: getattr(r, sorting_param)),
                )

    def test_sorting_descending(self):
        for sorting_param in self.sorting_params:
            with self.subTest(
                msg=f"Test sorting by {sorting_param}", sorting_param=sorting_param
            ):
                response = self.client.get(
                    reverse("list_recipes"),
                    data={"ordering": sorting_param, "is_descending": "on"},
                )
                self.assertEqual(
                    list(response.context["object_list"]),
                    sorted(
                        self.recipes,
                        key=lambda r: getattr(r, sorting_param),
                        reverse=True,
                    ),
                )
