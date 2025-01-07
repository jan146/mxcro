import os
from typing import Any
import requests
from bson import ObjectId
from user_info.src.models.converters.user_info_converter import UserInfoConverter
from user_info.src.models.entities.user_info import UserInfo

def check_serverless():
    url: str = f"{os.environ['SERVERLESS_NAMESPACE_URL']}/actions/health"
    params: dict[str, Any] = {
        "blocking": True,
        "result": True,
    }
    headers: dict[str, Any] = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {os.environ['SERVERLESS_AUTH']}",
    }
    response: requests.Response = requests.post(url=url, params=params, headers=headers, data="")
    if not response.ok:
        raise Exception(f"Error while executing serverless function: {response.status_code=}, {response.text=}")

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

    # Delete all user's logged items
    response: requests.Response = requests.delete(f"{os.environ['BACKEND_URL']}/api/v1/logged_item/user/{str(user.pk)}")
    if not response.ok:
        raise Exception(f"Failed to delete user's logged items: {response.status_code=}, {response.text=}")
    # Delete user
    return user.delete()

def create_user(data: dict[str, str]) -> UserInfo:
    if UserInfo.objects(username=data.get("username", "")):
        raise Exception(f"Failed to create user: username \"{data.get('username', '')}\" is already taken")
    user: UserInfo = UserInfoConverter.to_entity(data)
    user.save()
    return user

