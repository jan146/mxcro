from typing import Any
import requests
from requests import Response
import dotenv
import os
import json
from food_item.src.models.converters.food_item_converter import FoodItemConverter
from food_item.src.models.entities.food_item import FoodItem

RESPONSE_ENCODING: str = "utf-8"

dotenv.load_dotenv()

def get_nutrition_facts(query: str) -> list[FoodItem] | tuple[int, str]:
    api_key: str = os.environ["CALORIE_NINJAS_API_KEY"]
    url: str = "https://api.calorieninjas.com/v1/nutrition"
    params: dict[str, str] = {
        "query": query,
    }
    headers: dict[str, str] = {
        "X-Api-Key": api_key,
    }
    response: Response = requests.get(url, params=params, headers=headers)
    if response.ok:
        try:
            content: dict[str, Any] = json.loads(response.content.decode(RESPONSE_ENCODING))
        except Exception as e:
            return response.status_code, f"Failed to convert response to JSON: {str(e)}"
        try:
            return [FoodItemConverter.to_entity(food_item) for food_item in content["items"]]
        except KeyError as e:
            raise Exception(f"Error: Failed to convert food item from API response: {str(e)}")
    else:
        return response.status_code, response.text

if __name__ == "__main__":
    resp = get_nutrition_facts("100g yogurt")

