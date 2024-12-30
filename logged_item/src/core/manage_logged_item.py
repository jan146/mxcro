from typing import Any
from dotenv import load_dotenv
from food_item.src.models.converters.food_item_converter import FoodItemConverter
from food_item.src.models.entities.food_item import FoodItem
from logged_item.src.models.entities.logged_item import LoggedItem
from user_info.src.core.user_info import get_user_info
import requests
import os
import json
import time

RESPONSE_ENCODING: str = "utf-8"

load_dotenv()

def add_item_to_user(user_id: str, data: dict[str, str]) -> LoggedItem:
    
    # Parse request body
    food_name: str = data.get("food_name", "").strip()
    weight_str: str = data.get("weight", "").strip()
    if not food_name:
        raise Exception("Food name cannot be empty")
    if not weight_str:
        raise Exception("Weight cannot be empty")
    weight: int = 0
    try:
        weight = int(weight_str)
    except ValueError:
        raise Exception("Failed to cast weight to number")
    
    # Fetch food item from API
    response: requests.Response = requests.get(f"{os.environ['BACKEND_URL']}/food_item/{food_name}")
    if not response.ok:
        raise Exception(f"Failed to fetch food item: {response.status_code=}, {response.text=}")
    content: dict[str, Any] = json.loads(response.content.decode(RESPONSE_ENCODING))
    food_item_dict: dict[str, Any] = content["food_item"]
    food_item: FoodItem = FoodItemConverter.to_entity(food_item_dict)

    # Check if user exists
    response = requests.get(f"{os.environ['BACKEND_URL']}/user_info/{user_id}")
    if response.status_code == 404:
        raise Exception(f"User with id {user_id} does not exist")
    if not response.ok:
        raise Exception(f"Failed to check if user exists: {response.status_code=}, {response.text=}")

    # Create new logged item
    logged_item: LoggedItem = LoggedItem(
        timestamp=time.time(),
        quantity=weight,
        user_id=user_id,
        food_item_id=str(food_item.pk),
    )
    logged_item.save()
    return logged_item

