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
                response = self.client.get(
                    reverse("search_results"),
                    data={
                        "search_string": test_data["search_string"],
                        test_data["search_param"]: "on",
                    },
                )
                self.assertEqual(
                    sorted(r.pk for r in response.context["object_list"]),
                    sorted(r.pk for r in test_data["found"]),
                )


class CreateRecipeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="user", password="123456")

    def setUp(self):
        self.client.login(username="user", password="123456")

    def test_recipe_creation(self):
        response = self.client.post(
            reverse("create_recipe"),
            data={
                "name": "Test",
                "description": "test recipe",
                "cooking_time": 10,
                "category": "test",
                "new_ingredient_name": ["apple", "pear"],
                "new_ingredient_volume": [100, 1],
                "new_ingredient_volume_measure": ["g", "pcs"],
                "new_step_description": ["step 1", "step 2"],
                "new_tag_text": ["tag 1", "tag 2"],
            },
        )

        recipe = Recipe.objects.get(name="Test")
        ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        steps = RecipeStep.objects.filter(recipe=recipe)
        tags = RecipeTag.objects.filter(recipe=recipe)

        self.assertEqual(recipe.name, "Test")
        self.assertEqual(recipe.description, "test recipe")
        self.assertEqual(recipe.cooking_time, 10)
        self.assertEqual(recipe.category, "test")

        self.assertCountEqual([i.name for i in ingredients], ["apple", "pear"])
        self.assertCountEqual([i.volume for i in ingredients], [100, 1])
        self.assertCountEqual([i.volume_measure for i in ingredients], ["g", "pcs"])

        self.assertCountEqual([s.step_description for s in steps], ["step 1", "step 2"])

        self.assertCountEqual([t.tag_text for t in tags], ["tag 1", "tag 2"])


class EditRecipeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="user", password="123456")

        cls.recipe = Recipe.objects.create(
            user=cls.user,
            name="test 1",
            description="test",
            cooking_time=30,
            category="test a",
            created_at=datetime.datetime(2025, 1, 13, 14, 30),
            updated_at=datetime.datetime(2025, 1, 13, 15, 30),
        )

        cls.steps = [
            RecipeStep.objects.create(
                recipe=cls.recipe, step_number=0, step_description="s1"
            ),
            RecipeStep.objects.create(
                recipe=cls.recipe, step_number=1, step_description="s2"
            ),
        ]

        cls.ingredients = [
            RecipeIngredient.objects.create(
                recipe=cls.recipe, name="apple", volume=1.0, volume_measure="pcs"
            ),
            RecipeIngredient.objects.create(
                recipe=cls.recipe, name="pear", volume=1.0, volume_measure="pcs"
            ),
        ]

        cls.tags = [
            RecipeTag.objects.create(recipe=cls.recipe, tag_text="tag 1"),
            RecipeTag.objects.create(recipe=cls.recipe, tag_text="tag 2"),
        ]

        cls.post_data = {
            "name": "Test",
            "description": "test recipe",
            "cooking_time": 10,
            "category": "test",
            "recipestep_set-TOTAL_FORMS": "2",
            "recipestep_set-INITIAL_FORMS": "2",
            "recipestep_set-0-id": cls.steps[0].pk,
            "recipestep_set-0-step_description": "step 1",
            "recipestep_set-0-DELETE": "",
            "recipestep_set-1-id": cls.steps[1].pk,
            "recipestep_set-1-step_description": cls.steps[1].step_description,
            "recipestep_set-1-DELETE": "on",
            "new_step_description": ["step 3"],
            "recipeingredient_set-TOTAL_FORMS": "2",
            "recipeingredient_set-INITIAL_FORMS": "2",
            "recipeingredient_set-0-id": cls.ingredients[0].pk,
            "recipeingredient_set-0-name": "McIntosh apple",
            "recipeingredient_set-0-volume": "200",
            "recipeingredient_set-0-volume_measure": "g",
            "recipeingredient_set-0-DELETE": "",
            "recipeingredient_set-1-id": cls.ingredients[1].pk,
            "recipeingredient_set-1-name": cls.ingredients[1].name,
            "recipeingredient_set-1-volume": cls.ingredients[1].volume,
            "recipeingredient_set-1-volume_measure": cls.ingredients[1].volume_measure,
            "recipeingredient_set-1-DELETE": "on",
            "new_ingredient_name": ["strawberry"],
            "new_ingredient_volume": [1],
            "new_ingredient_volume_measure": ["pcs"],
            "recipetag_set-TOTAL_FORMS": "2",
            "recipetag_set-INITIAL_FORMS": "2",
            "recipetag_set-0-id": cls.tags[0].pk,
            "recipetag_set-0-tag_text": "tag 1 updated",
            "recipetag_set-0-DELETE": "",
            "recipetag_set-1-id": cls.tags[1].pk,
            "recipetag_set-1-tag_text": cls.tags[1].tag_text,
            "recipetag_set-1-DELETE": "on",
            "new_tag_text": ["tag 3"],
        }

    def setUp(self):
        self.client.login(username="user", password="123456")
    
    def test_recipe_editing(self):
        self.client.post(reverse("edit_recipe", kwargs={"recipe_id": self.recipe.pk}), data=self.post_data)

        recipe = Recipe.objects.get(pk=self.recipe.pk)
        ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        steps = RecipeStep.objects.filter(recipe=recipe)
        tags = RecipeTag.objects.filter(recipe=recipe)

        self.assertEqual(recipe.name, "Test")
        self.assertEqual(recipe.description, "test recipe")
        self.assertEqual(recipe.cooking_time, 10)
        self.assertEqual(recipe.category, "test")

        self.assertCountEqual([i.name for i in ingredients], ["McIntosh apple", "strawberry"])
        self.assertCountEqual([i.volume for i in ingredients], [200, 1])
        self.assertCountEqual([i.volume_measure for i in ingredients], ["g", "pcs"])

        self.assertCountEqual([s.step_description for s in steps], ["step 1", "step 3"])

        self.assertCountEqual([t.tag_text for t in tags], ["tag 1 updated", "tag 3"])
