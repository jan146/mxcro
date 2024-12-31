from typing import Any
from food_item.src.models.entities.food_item import FoodItem

WEIGHT_DEFAULT: float = 100.0

def get_multiple_keys(dictionary: dict[Any, Any], keys: list[Any]) -> Any:
    for key in keys:
        if dictionary.get(key) is not None:
            return dictionary[key]
    raise KeyError(f"None of the following keys were present: {str(keys)}")

class FoodItemConverter():
    @staticmethod
    def to_entity(content: dict[str, Any], normalized_weight: bool = True, quantity_multiplier: float = 1.0) -> FoodItem:
        weight_g: float = get_multiple_keys(content, ["serving_size_g", "weight_g"])
        normalization_multiplier: float = WEIGHT_DEFAULT / weight_g if normalized_weight else 1.0
        multiplier: float = normalization_multiplier * quantity_multiplier
        food_item_entity: FoodItem = FoodItem(
            id=content.get("id", None),
            name=content["name"].lower(),
            calories=(content["calories"] * multiplier),
            weight_g=WEIGHT_DEFAULT if normalized_weight else weight_g,
            fat_total=(get_multiple_keys(content, ["fat_total_g", "fat_total"]) * multiplier),
            fat_saturated=(get_multiple_keys(content, ["fat_saturated_g", "fat_saturated"]) * multiplier),
            protein=(get_multiple_keys(content, ["protein_g", "protein"]) * multiplier),
            carbohydrates=(get_multiple_keys(content, ["carbohydrates_total_g", "carbohydrates"]) * multiplier),
            fiber=(get_multiple_keys(content, ["fiber_g", "fiber"]) * multiplier),
            sugar=(get_multiple_keys(content, ["sugar_g", "sugar"]) * multiplier),
            sodium=(get_multiple_keys(content, ["sodium_mg", "sodium"]) * multiplier),
            potassium=(get_multiple_keys(content, ["potassium_mg", "potassium"]) * multiplier),
            cholesterol=(get_multiple_keys(content, ["cholesterol_mg", "cholesterol"]) * multiplier),
        )
        return food_item_entity
    @staticmethod
    def to_dict(entity: FoodItem, normalized_weight: bool = True, quantity_multiplier: float = 1.0) -> dict[str, Any]:
        normalization_multiplier: float = WEIGHT_DEFAULT / entity.weight_g if normalized_weight else 1.0
        multiplier: float = normalization_multiplier * quantity_multiplier
        return {
            "id": str(entity.pk),
            "name": entity.name,
            "calories": (entity.calories * multiplier),
            "weight_g": (entity.weight_g * multiplier),
            "fat_total": (entity.fat_total * multiplier),
            "fat_saturated": (entity.fat_saturated * multiplier),
            "protein": (entity.protein * multiplier),
            "carbohydrates": (entity.carbohydrates * multiplier),
            "fiber": (entity.fiber * multiplier),
            "sugar": (entity.sugar * multiplier),
            "sodium": (entity.sodium * multiplier),
            "potassium": (entity.potassium * multiplier),
            "cholesterol": (entity.cholesterol * multiplier),
        }

