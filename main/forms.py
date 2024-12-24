from django.forms import ModelForm, modelformset_factory

from .models import Recipe, RecipeIngredient, RecipeStep, RecipeTag


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ["name", "description", "cooking_time", "category"]

        labels = {
            "name": "Назва страви",
            "description": "Опис",
            "cooking_time": "Час приготування, хв",
            "category": "Категорія",
        }


class RecipeIngredientForm(ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ["name", "volume", "volume_measure"]


class RecipeStepForm(ModelForm):
    class Meta:
        model = RecipeStep
        fields = ["step_description"]

class RecipeStepEditingForm(ModelForm):
    class Meta:
        model = RecipeStep
        fields = ["step_number", "step_description"]


class RecipeTagForm(ModelForm):
    class Meta:
        model = RecipeTag
        fields = ["tag_text"]


RecipeStepFormSet = modelformset_factory(
    RecipeStep, 
    fields=('step_number', 'step_description'),
    # can_delete=True
)


RecipeTagFormSet = modelformset_factory(
    RecipeTag, 
    fields=('tag_text',),
    # can_delete=True
)


RecipeIngredientFormSet = modelformset_factory(
    RecipeIngredient,
    fields=('name', 'volume', 'volume_measure'),
    # can_delete=True
)
