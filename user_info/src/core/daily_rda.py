import os
from typing import Any
import requests
from user_info.src.models.entities.user_info import UserInfo
import json

def get_daily_rda(user: UserInfo) -> dict[str, Any]:
    url: str = f"{os.environ['SERVERLESS_NAMESPACE_URL']}/actions/get_daily_rda"
    params: dict[str, Any] = {
        "blocking": True,
        "result": True,
    }
    headers: dict[str, Any] = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {os.environ['SERVERLESS_AUTH']}",
    }
    data: dict[str, Any] = {
        "age": user.age,
        "height": user.height,
        "weight": user.weight,
        "gender": user.gender.value,
        "activity_level": user.activity_level.value,
    }
    response: requests.Response = requests.post(url=url, params=params, headers=headers, data=json.dumps(data))
    if not response.ok:
        raise Exception(f"Failed to get daily RDA for user with id {str(user.pk)}: {response.status_code=}, {response.text=}")
    return json.loads(response.text)

