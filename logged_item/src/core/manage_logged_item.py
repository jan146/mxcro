from typing import Any
from bson import ObjectId
from dotenv import load_dotenv
from food_item.src.models.converters.food_item_converter import FoodItemConverter
from food_item.src.models.entities.food_item import FoodItem
from logged_item.src.models.entities.logged_item import LoggedItem
import requests
import os
import json
import datetime

RESPONSE_ENCODING: str = "utf-8"

load_dotenv()

def add_item_to_user(user_id: str, date: datetime.date, data: dict[str, str]) -> LoggedItem | None:
    
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
    response: requests.Response = requests.get(f"{os.environ['BACKEND_URL']}/api/v1/food_item/{food_name}")
    if not response.ok:
        raise Exception(f"Failed to fetch food item: {response.status_code=}, {response.text=}")
    if not response.content:
        return None
    content: dict[str, Any] = json.loads(response.content.decode(RESPONSE_ENCODING))
    food_item_dict: dict[str, Any] = content["food_item"]
    food_item: FoodItem = FoodItemConverter.to_entity(food_item_dict)

    # Check if user exists
    response = requests.get(f"{os.environ['BACKEND_URL']}/api/v1/user_info/id/{user_id}")
    if response.status_code == 404:
        raise Exception(f"User with id {user_id} does not exist")
    if not response.ok:
        raise Exception(f"Failed to check if user exists: {response.status_code=}, {response.text=}")
    
    # Create arbitrary timestamp on specified date
    timestamp: float = datetime.datetime(date.year, date.month, date.day, 12, 0, 0).timestamp()
    
    # Create new logged item
    logged_item: LoggedItem = LoggedItem(
        timestamp=timestamp,
        quantity=weight,
        user_id=user_id,
        food_item_id=str(food_item.pk),
    )
    logged_item.save()
    return logged_item

def get_logged_items(user_id: str, from_date: datetime.date, to_date: datetime.date) -> list[dict[str, Any]]:

    # Check if user exists
    response = requests.get(f"{os.environ['BACKEND_URL']}/api/v1/user_info/id/{user_id}")
    if response.status_code == 404:
        raise Exception(f"User with id {user_id} does not exist")
    if not response.ok:
        raise Exception(f"Failed to check if user exists: {response.status_code=}, {response.text=}")

    # Get list of logged items
    from_timestamp: float = datetime.datetime(from_date.year, from_date.month, from_date.day, 0, 0, 0).timestamp()
    to_timestamp: float = datetime.datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59).timestamp()
    logged_items: list[LoggedItem] = list(LoggedItem.objects(
        user_id=user_id,
        timestamp__gte=from_timestamp,
        timestamp__lte=to_timestamp,
    ))
    
    # Build list of logged items
    logged_items_list: list[dict[str, Any]] = []
    for logged_item in logged_items:
        food_item: FoodItem | None = logged_item_to_food_item(logged_item)
        if food_item is None:
            raise Exception(f"Failed to find {logged_item.food_item_id=}")
        food_item_dict: dict[str, Any] = FoodItemConverter.to_dict(food_item, normalized_weight=True, quantity_multiplier=logged_item.quantity/100.0)
        food_item_dict["id"] = str(logged_item.pk)
        logged_items_list.append(food_item_dict)
    return logged_items_list

def logged_item_to_food_item(logged_item: LoggedItem) -> FoodItem | None:
    # Maybe do a requery if this specific food item is no longer present in database?
    food_items: list[FoodItem] = list(FoodItem.objects(pk=ObjectId(logged_item.food_item_id)))
    return food_items[0] if food_items else None

def delete_logged_item(logged_item_id: str) -> bool:
    logged_items: list[LoggedItem] = list(LoggedItem.objects(pk=ObjectId(logged_item_id)))
    if not logged_items:
        return False
    logged_items[0].delete()
    return True

def delete_logged_items_for_user(user_id: str):
    return LoggedItem.objects(user_id=user_id).delete()

