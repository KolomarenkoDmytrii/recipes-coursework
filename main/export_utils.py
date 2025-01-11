from io import BytesIO


def export_recipe_to_text(recipe, ingredients, steps, tags):
    text = f"{recipe.name}\n\
=====\n\
\n\
Інформація\n\
-----\n\
Опис: {recipe.description}\n\
Час приготування, хв: {recipe.cooking_time}\n\
Категорія: {recipe.category}\n\
\n\
Інгредієнти\n\
-----\n"

    for ingredient in ingredients:
        text += (
            f"- {ingredient.name}: {ingredient.volume} {ingredient.volume_measure}\n"
        )

    text += "\nКроки\n-----\n"
    for number, step in enumerate(sorted(steps, key=lambda s: s.step_number), start=1):
        text += f"{number}) {step.step_description}\n"

    text += "\nТеги\n-----\n"
    for tag in tags:
        text += f"- {tag.tag_text}\n"

    return BytesIO(bytes(text, encoding="utf-8"))
