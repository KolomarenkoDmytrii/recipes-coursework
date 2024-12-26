from django.forms import ModelForm, modelformset_factory, inlineformset_factory

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

class RecipeTagForm(ModelForm):
    class Meta:
        model = RecipeTag
        fields = ["tag_text"]


# RecipeStepFormSet = modelformset_factory(
#     model=RecipeStep, 
#     form=RecipeStepForm,
#     # fields=('step_number', 'step_description'),
#     fields=("step_description",),
#     can_delete=True,
#     extra=0,
# )


# RecipeTagFormSet = modelformset_factory(
#     model=RecipeTag,
#     form=RecipeTagForm, 
#     fields=("tag_text",),
#     can_delete=True,
#     extra=0,
# )


# RecipeIngredientFormSet = modelformset_factory(
#     model=RecipeIngredient,
#     form=RecipeIngredientForm,
#     fields=("name", "volume", "volume_measure"),
#     can_delete=True,
#     extra=0,
# )

RecipeStepFormSet = inlineformset_factory(
    parent_model=Recipe, 
    model=RecipeStep,
    fields=["step_description"],
    can_delete=True,
    extra=0,
    labels={
        "step_description": "Опис кроку",
    }
)


RecipeTagFormSet = inlineformset_factory(
    parent_model=Recipe,
    model=RecipeTag, 
    fields=["tag_text"],
    can_delete=True,
    extra=0,
)


RecipeIngredientFormSet = inlineformset_factory(
    parent_model=Recipe,
    model=RecipeIngredient,
    fields=["name", "volume", "volume_measure"],
    can_delete=True,
    extra=0,
)
