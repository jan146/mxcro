from typing import Any
from food_item.src.models.entities.food_item import FoodItem

WEIGHT_DEFAULT: float = 100.0

def get_multiple_keys(dictionary: dict[Any, Any], keys: list[Any]) -> Any:
    for key in keys:
        if dictionary.get(key):
            return dictionary[key]
    raise KeyError(f"None of the following keys were present: {str(keys)}")

class FoodItemConverter():
    @staticmethod
    def to_entity(content: dict[str, Any], normalized_weight: bool = True) -> FoodItem:
        weight_g: float = get_multiple_keys(content, ["serving_size_g", "weight_g"])
        normalization_multiplier: float = WEIGHT_DEFAULT / weight_g if normalized_weight else 1.0
        food_item_entity: FoodItem = FoodItem(
            id=content.get("id", None),
            name=content["name"].lower(),
            calories=(content["calories"] * normalization_multiplier),
            weight_g=WEIGHT_DEFAULT if normalized_weight else weight_g,
            fat_total=(get_multiple_keys(content, ["fat_total_g", "fat_total"]) * normalization_multiplier),
            fat_saturated=(get_multiple_keys(content, ["fat_saturated_g", "fat_saturated"]) * normalization_multiplier),
            protein=(get_multiple_keys(content, ["protein_g", "protein"]) * normalization_multiplier),
            carbohydrates=(get_multiple_keys(content, ["carbohydrates_total_g", "carbohydrates"]) * normalization_multiplier),
            fiber=(get_multiple_keys(content, ["fiber_g", "fiber"]) * normalization_multiplier),
            sugar=(get_multiple_keys(content, ["sugar_g", "sugar"]) * normalization_multiplier),
            sodium=(get_multiple_keys(content, ["sodium_mg", "sodium"]) * normalization_multiplier),
            potassium=(get_multiple_keys(content, ["potassium_mg", "potassium"]) * normalization_multiplier),
            cholesterol=(get_multiple_keys(content, ["cholesterol_mg", "cholesterol"]) * normalization_multiplier),
        )
        return food_item_entity
    @staticmethod
    def to_dict(entity: FoodItem) -> dict[str, Any]:
        return {
            "id": str(entity.pk),
            "name": entity.name,
            "calories": entity.calories,
            "weight_g": entity.weight_g,
            "fat_total": entity.fat_total,
            "fat_saturated": entity.fat_saturated,
            "protein": entity.protein,
            "carbohydrates": entity.carbohydrates,
            "fiber": entity.fiber,
            "sugar": entity.sugar,
            "sodium": entity.sodium,
            "potassium": entity.potassium,
            "cholesterol": entity.cholesterol,
        }

