from typing import Any

from user_info.src.models.entities.user_info import UserInfo

WEIGHT_DEFAULT: float = 100.0

class UserInfoConverter():
    @staticmethod
    def to_dict(entity: UserInfo) -> dict[str, Any]:
        return {
            "id": str(entity.pk),
            "username": entity.username,
            "age": entity.age,
            "height": entity.height,
            "weight": entity.weight,
        }

