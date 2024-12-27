from typing import Any
from food_item.src.models.entities.food_item import FoodItem

class FoodItemConverter():
    @staticmethod
    def to_entity(content: dict[str, Any]) -> FoodItem:
        food_item: FoodItem = FoodItem(
            name=content["name"].lower(),
            calories=content["calories"],
            weight_g=content["serving_size_g"],
            fat_total=content["fat_total_g"],
            fat_saturated=content["fat_saturated_g"],
            protein=content["protein_g"],
            carbohydrates=content["carbohydrates_total_g"],
            fiber=content["fiber_g"],
            sugar=content["sugar_g"],
            sodium=content["sodium_mg"],
            potassium=content["potassium_mg"],
            cholesterol=content["cholesterol_mg"],
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

