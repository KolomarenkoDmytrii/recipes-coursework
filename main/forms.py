from django import forms

from .models import Recipe, RecipeIngredient, RecipeStep, RecipeTag


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            "name",
            "description",
            "cooking_time",
            "category",
            "image_1",
            "image_2",
            "image_3",
        ]

        labels = {
            "name": "Назва страви",
            "description": "Опис",
            "cooking_time": "Час приготування, хв",
            "category": "Категорія",
            "image_1": "Зображення страви (1)",
            "image_2": "Зображення страви (2)",
            "image_3": "Зображення страви (3)",
        }


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["name", "volume", "volume_measure"]


class RecipeStepForm(forms.ModelForm):
    class Meta:
        model = RecipeStep
        fields = ["step_description"]


class RecipeTagForm(forms.ModelForm):
    class Meta:
        model = RecipeTag
        fields = ["tag_text"]


RecipeStepFormSet = forms.inlineformset_factory(
    parent_model=Recipe,
    model=RecipeStep,
    fields=["step_description"],
    can_delete=True,
    extra=0,
    labels={
        "step_description": "Опис кроку",
    },
)


RecipeTagFormSet = forms.inlineformset_factory(
    parent_model=Recipe,
    model=RecipeTag,
    fields=["tag_text"],
    can_delete=True,
    extra=0,
    labels={"tag_text": "Тег"},
)


RecipeIngredientFormSet = forms.inlineformset_factory(
    parent_model=Recipe,
    model=RecipeIngredient,
    fields=["name", "volume", "volume_measure"],
    can_delete=True,
    extra=0,
    labels={
        "name": "Назва інгредієнту",
        "volume": "Обсяг",
        "volume_measure": "Міра обсягу",
    },
)


class SearchForm(forms.Form):
    search_string = forms.CharField(required=True, label="Пошук")
    search_in_names = forms.BooleanField(
        initial=True, required=False, label="Шукати за іменем"
    )
    search_in_descriptions = forms.BooleanField(
        required=False, label="Шукати за описом"
    )
    search_in_ingredients = forms.BooleanField(
        required=False, label="Шукати за інгредієнтом"
    )
    search_in_categories = forms.BooleanField(
        required=False, label="Шукати за категорією"
    )
    search_in_tags = forms.BooleanField(required=False, label="Шукати за тегом")


class RecipeGenerationForm(forms.Form):
    ingredients_description = forms.CharField(required=True, label="Опис інгредієнтів")
    recipe_description = forms.CharField(required=True, label="Опис рецепту")


class SortRecipeListForm(forms.Form):
    ordering = forms.ChoiceField(
        choices=[
            ("name", "За назвою"),
            ("cooking_time", "За часом приготування"),
            ("category", "За категорією"),
            ("created_at", "За часом створення"),
            ("updated_at", "За часом оновлення"),
        ],
        label="За чим сортувати",
        initial="name",
    )
    is_descending = forms.BooleanField(required=False, label="У спадному порядку")
