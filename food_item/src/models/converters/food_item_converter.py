from typing import Any
from food_item.src.models.entities.food_item import FoodItem

WEIGHT_DEFAULT: float = 100.0

class FoodItemConverter():
    @staticmethod
    def to_entity(content: dict[str, Any], normalized_weight: bool = True) -> FoodItem:
        weight_g: float = content["serving_size_g"]
        normalization_multiplier: float = WEIGHT_DEFAULT / weight_g if normalized_weight else 1.0
        food_item: FoodItem = FoodItem(
            name=content["name"].lower(),
            calories=(content["calories"] * normalization_multiplier),
            weight_g=WEIGHT_DEFAULT if normalized_weight else weight_g,
            fat_total=(content["fat_total_g"] * normalization_multiplier),
            fat_saturated=(content["fat_saturated_g"] * normalization_multiplier),
            protein=(content["protein_g"] * normalization_multiplier),
            carbohydrates=(content["carbohydrates_total_g"] * normalization_multiplier),
            fiber=(content["fiber_g"] * normalization_multiplier),
            sugar=(content["sugar_g"] * normalization_multiplier),
            sodium=(content["sodium_mg"] * normalization_multiplier),
            potassium=(content["potassium_mg"] * normalization_multiplier),
            cholesterol=(content["cholesterol_mg"] * normalization_multiplier),
        )
        return food_item
    @staticmethod
    def to_dict(entity: FoodItem) -> dict[str, Any]:
        return {
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

