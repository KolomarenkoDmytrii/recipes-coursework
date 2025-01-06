import json

import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

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
