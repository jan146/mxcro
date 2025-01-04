from bson import ObjectId
from user_info.src.models.converters.user_info_converter import UserInfoConverter
from user_info.src.models.entities.user_info import UserInfo

def get_user_info(id: str) -> UserInfo | None:
    try:
        user_infos: list[UserInfo] | None = list(UserInfo.objects(pk=ObjectId(id)))
    except Exception as e:
        return None
    if user_infos:
        return user_infos[0]
    else:
        return None

def get_user_info_by_username(username: str) -> UserInfo | None:
    try:
        user_infos: list[UserInfo] | None = list(UserInfo.objects(username=username))
    except Exception as e:
        return None
    if user_infos:
        return user_infos[0]
    else:
        return None

def delete_user(user: UserInfo):
    return user.delete()

def create_user(data: dict[str, str]) -> UserInfo:
    user: UserInfo = UserInfoConverter.to_entity(data)
    user.save()
    return user

