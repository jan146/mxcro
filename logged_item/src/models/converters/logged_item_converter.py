from typing import Any
from logged_item.src.models.entities.logged_item import LoggedItem

class LoggedItemConverter():
    @staticmethod
    def to_entity(content: dict[str, Any]) -> LoggedItem:
        logged_item_entity: LoggedItem = LoggedItem(
            timestamp=float(content["timestamp"]),
            quantity=float(content["quantity"]),
            user_id=content["user_id"],
            food_item_id=content["food_item_id"],
        )
        return logged_item_entity
    @staticmethod
    def to_dict(entity: LoggedItem) -> dict[str, Any]:
        return {
            "id": str(entity.pk),
            "timestamp": entity.timestamp,
            "quantity": entity.quantity,
            "user_id": entity.user_id,
            "food_item_id": entity.food_item_id,
        }

