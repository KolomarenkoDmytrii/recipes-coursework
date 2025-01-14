import datetime

from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth.models import User
from .models import Recipe, RecipeIngredient, RecipeStep, RecipeTag


class ListRecipesViewTest(TestCase):
    SORTING_PARAMS = ["name", "cooking_time", "category", "created_at", "updated_at"]

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
        for sorting_param in self.SORTING_PARAMS:
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
        for sorting_param in self.SORTING_PARAMS:
            with self.subTest(
                msg=f"Test sorting by {sorting_param} in descending order",
                sorting_param=sorting_param,
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


class SearchViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="user", password="123456")

        recipe_1 = Recipe.objects.create(
            user=cls.user,
            name="test 1",
            description="test",
            cooking_time=30,
            category="test a",
            created_at=datetime.datetime(2025, 1, 13, 14, 30),
            updated_at=datetime.datetime(2025, 1, 13, 15, 30),
        )
        recipe_2 = Recipe.objects.create(
            user=cls.user,
            name="test 2",
            description="test",
            cooking_time=30,
            category="test b",
            created_at=datetime.datetime(2025, 1, 13, 14, 30),
            updated_at=datetime.datetime(2025, 1, 13, 15, 30),
        )

        cls.data = {
            "recipe_1": {
                "recipe": recipe_1,
                "ingredients": [
                    RecipeIngredient.objects.create(
                        recipe=recipe_1, name="apple", volume=1.0, volume_measure="pcs"
                    )
                ],
                "tags": [RecipeTag.objects.create(recipe=recipe_1, tag_text="tag")],
            },
            "recipe_2": {
                "recipe": recipe_2,
                "ingredients": [
                    RecipeIngredient.objects.create(
                        recipe=recipe_2,
                        name="strawberry",
                        volume=3.0,
                        volume_measure="pcs",
                    )
                ],
                "tags": [RecipeTag.objects.create(recipe=recipe_2, tag_text="tag")],
            },
        }

        cls.TEST_DATA = [
            {
                "search_param": "search_in_names",
                "search_string": "test 1",
                "found": [recipe_1],
            },
            {
                "search_param": "search_in_descriptions",
                "search_string": "test",
                "found": [recipe_1, recipe_2],
            },
            {
                "search_param": "search_in_categories",
                "search_string": "b",
                "found": [recipe_2],
            },
            {
                "search_param": "search_in_ingredients",
                "search_string": "apple",
                "found": [recipe_1],
            },
            {
                "search_param": "search_in_tags",
                "search_string": "tag",
                "found": [recipe_1, recipe_2],
            },
        ]

    def setUp(self):
        self.client.login(username="user", password="123456")

    def test_search(self):
        for test_data in self.TEST_DATA:
            with self.subTest(
                msg=f"Test search by param '{test_data['search_param']}' and search string '{test_data['search_string']}'",
                search_param=test_data["search_param"],
                search_string=test_data["search_string"],
                found=test_data["found"],
            ):
                response = self.client.get(reverse("search_results"), data={"search_string": test_data["search_string"], test_data["search_param"]: "on"})
                self.assertEqual(sorted(r.pk for r in response.context["object_list"]), sorted(r.pk for r in test_data["found"]))
