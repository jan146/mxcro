from typing import Any
from user_info.src.models.entities.user_info import UserInfo, Gender, ActivityLevel

class UserInfoConverter():
    @staticmethod
    def to_entity(content: dict[str, Any]) -> UserInfo:
        user_info_entity: UserInfo = UserInfo(
            id=content.get("id", None),
            username=content["username"],
            age=content["age"],
            height=content["height"],
            weight=content["weight"],
            gender=Gender(content["gender"]),
            activity_level=ActivityLevel(content["activity_level"]),
        )
        return user_info_entity
    @staticmethod
    def to_dict(entity: UserInfo) -> dict[str, Any]:
        return {
            "id": str(entity.pk),
            "username": entity.username,
            "age": entity.age,
            "height": entity.height,
            "weight": entity.weight,
            "gender": entity.gender.value,
            "activity_level": entity.activity_level.value,
        }

