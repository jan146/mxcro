from bson import ObjectId
from user_info.src.models.entities.user_info import UserInfo

def get_user_info(id: str) -> UserInfo | None:
    try:
        user_infos: list[UserInfo] | None = UserInfo.objects(pk=ObjectId(id))
    except Exception as e:
        return None
    if user_infos:
        return user_infos[0]
    else:
        return None

def get_user_info_by_username(username: str) -> UserInfo | None:
    try:
        user_infos: list[UserInfo] | None = UserInfo.objects(username=username)
    except Exception as e:
        return None
    if user_infos:
        return user_infos[0]
    else:
        return None

def create_user(data: dict[str, str]) -> UserInfo:
    user: UserInfo = UserInfo(
        username=data["username"],
        age=data["age"],
        height=data["height"],
        weight=data["weight"],
    )
    user.save()
    return user

