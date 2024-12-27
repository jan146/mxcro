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

def check_existing_records(query: str) -> FoodItem | None:
    result: list[FoodItem] | None = FoodItem.objects(name=query.lower())
    return result[0] if result else None

def get_nutrition_facts(query: str) -> FoodItem | tuple[int, str]:
    cached_record: FoodItem | None = check_existing_records(query)
    if cached_record:
        return cached_record
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
        if len(content["items"]) < 1:
            return 204, response.text
        try:
            food_item: FoodItem = FoodItemConverter.to_entity(content["items"][0])
            food_item.save()
            return food_item
        except KeyError as e:
            raise Exception(f"Error: Failed to convert food item from API response: {str(e)}")
    else:
        return response.status_code, response.text

if __name__ == "__main__":
    resp = get_nutrition_facts("100g yogurt")

