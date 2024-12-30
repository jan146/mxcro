from typing import Any
from logged_item.src.models.entities.logged_item import LoggedItem

class LoggedItemConverter():
    @staticmethod
    def to_dict(entity: LoggedItem) -> dict[str, Any]:
        return {
            "id": str(entity.pk),
            "timestamp": entity.timestamp,
            "quantity": entity.quantity,
            "user_id": entity.user_id,
            "food_item_id": entity.food_item_id,
        }

