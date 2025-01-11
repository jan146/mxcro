from typing import Any, cast
import requests
from requests import Response
import dotenv
import os
import json
import time
from food_item.src.core.fault_tolerance import get_cb_state, get_latest_cb, trip_cb, update_half_open_cb
from food_item.src.models.converters.food_item_converter import FoodItemConverter
from food_item.src.models.entities.circuit_breaker import CircuitBreaker, CircuitBreakerState
from food_item.src.models.entities.food_item import FoodItem

RESPONSE_ENCODING: str = "utf-8"
EXTERNAL_API_RETRY: int = 3
EXTERNAL_API_DELAY: int = 3
EXTERNAL_API_EVENT_NAME: str = "calorie_ninjas_api"

dotenv.load_dotenv()

def check_existing_records(query: str) -> FoodItem | None:
    result: list[FoodItem] | None = FoodItem.objects(name=query.lower())
    return result[0] if result else None

def check_calorie_ninjas_api_status():
    # Sadly, it doesn't have ANY status/health endpoint
    url: str = "https://api.calorieninjas.com"
    try:
        requests.get(url=url, timeout=5)
    except Exception as e:
        raise Exception(f"Timeout reached when reaching Calorie Ninjas API {str(e)}")

def get_nutrition_facts(query: str) -> FoodItem | tuple[str, int]:
    # Return cached record if it exists
    cached_record: FoodItem | None = check_existing_records(query)
    if cached_record:
        return cached_record

    # Prepare request data
    api_key: str = os.environ["CALORIE_NINJAS_API_KEY"]
    url: str = "https://api.calorieninjas.com/v1/nutrition"
    params: dict[str, str] = {
        "query": query,
    }
    headers: dict[str, str] = {
        "X-Api-Key": api_key,
    }

    # Check circuit breaker status
    cb: CircuitBreaker | None = get_latest_cb(event_name=EXTERNAL_API_EVENT_NAME)
    cb_state: CircuitBreakerState = get_cb_state(cb)
    if cb_state == CircuitBreakerState.OPEN:
        return "Error: circuit breaker is tripped", 503

    # Try to get response from external API
    response_internal: FoodItem | tuple[str, int] | None = None
    response_error: tuple[str, int] | None = None
    for retry in range(EXTERNAL_API_RETRY):
        try:
            response_external: Response = requests.get(url, params=params, headers=headers)
            if response_external.ok:
                try:
                    content: dict[str, Any] = json.loads(response_external.content.decode(RESPONSE_ENCODING))
                except Exception as e:
                    response_internal = f"Failed to convert response to JSON: {str(e)}", 500
                    break
                if len(content["items"]) < 1:
                    response_internal = response_external.text, 404
                    break
                try:
                    food_item: FoodItem = FoodItemConverter.to_entity(content["items"][0])
                    if not check_existing_records(food_item.name):
                        food_item.save()
                    response_internal = food_item
                    break
                except KeyError as e:
                    response_internal = f"Error: Failed to convert food item from API response: {str(e)}", 500
                    break
            else:
                response_error = response_external.text, response_external.status_code
        except Exception as e:
            response_error = str(e), 500
        time.sleep(EXTERNAL_API_DELAY)

    if response_internal is None:
        # Failed to get valid response from API
        if cb_state == CircuitBreakerState.CLOSED or cb is None:
            trip_cb(EXTERNAL_API_EVENT_NAME)
        elif cb_state == CircuitBreakerState.HALF_OPEN:
            update_half_open_cb(cb, success=False)
        return cast(tuple[str, int], response_error)
    else:
        # Response was successful
        if cb_state == CircuitBreakerState.HALF_OPEN and cb is not None:
            update_half_open_cb(cb, success=True)
        return response_internal

