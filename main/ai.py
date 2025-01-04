import json

# from django.conf import settings

import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

# genai.configure(api_key=settings.GEMINI_API_KEY)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_schema": content.Schema(
        type=content.Type.OBJECT,
        enum=[],
        required=[
            "name",
            "description",
            "cooking_time_in_minutes",
            "category",
            "steps",
            "ingredients",
        ],
        properties={
            "name": content.Schema(
                type=content.Type.STRING,
            ),
            "description": content.Schema(
                type=content.Type.STRING,
            ),
            "cooking_time_in_minutes": content.Schema(
                type=content.Type.INTEGER,
            ),
            "category": content.Schema(
                type=content.Type.STRING,
            ),
            "steps": content.Schema(
                type=content.Type.ARRAY,
                items=content.Schema(
                    type=content.Type.STRING,
                ),
            ),
            "ingredients": content.Schema(
                type=content.Type.ARRAY,
                items=content.Schema(
                    type=content.Type.OBJECT,
                    enum=[],
                    required=["name", "volume", "volume_measure"],
                    properties={
                        "name": content.Schema(
                            type=content.Type.STRING,
                        ),
                        "volume": content.Schema(
                            type=content.Type.NUMBER,
                        ),
                        "volume_measure": content.Schema(
                            type=content.Type.STRING,
                        ),
                    },
                ),
            ),
        },
    ),
    "response_mime_type": "application/json",
}


def get_generated_recipe(ingredients_description, recipe_description):
    prompt = (
        f'Create a such recipe where ingredients can be described as "{ingredients_description}"'
        + f'and this recipe itself can be described as "{recipe_description}". '
        + "Output must be in Ukranian. Cooking steps must be without list item numbers."
    )

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    response = model.generate_content(prompt)
    return json.loads(response.text)


#     return json.loads(
#         '{"category": "Обсмажена риба", "cooking_time_in_minutes": 20, "description": \
# "Смачний рецепт обсмаженої риби з хрусткою скоринкою.", "ingredients": [{"name": \
# "Риб\'яче філе", "volume": 500, "volume_measure": "г"}, {"name": "Яйце", "volume": 2, \
# "volume_measure": "шт"}, {"name": "Борошно", "volume": 100, "volume_measure": "г"}], \
# "name": "Обсмажена риба", "steps": ["Підготуйте риб\'яче філе: вимийте, \
# обсушіть паперовим рушником та наріжте на порційні шматки.", \
# "У мисці збийте яйця виделкою.", "У іншій мисці насипте борошно.", \
# "Обваляйте кожен шматок риби спочатку в борошні, потім в яйці.", "Розігрійте олію \
# на сковороді на середньому вогні.", "Обсмажте рибу з обох боків до золотистої скоринки \
# (по 3-4 хвилини з кожного боку).", "Готову рибу викладіть на паперовий рушник, \
# щоб увібрався зайвий жир.", "Подавайте гарячою з улюбленим гарніром."]}'
#     )
