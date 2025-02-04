from typing import Any
from flask.testing import FlaskClient
from werkzeug.test import TestResponse
from food_item.src.api.v1.api import app as app_food_item
from logged_item.src.api.v1.api import app as app_logged_item
from user_info.src.api.v1.api import app as app_user_info
import pytest
from pymongo.synchronous.database import Database
from pymongo.synchronous.mongo_client import MongoClient
from mongoengine import disconnect_all, connect
from dotenv import load_dotenv
import os
import responses
import requests
import re

TEST_FOOD: str = "Apple"
TEST_USER: dict[str, Any] = {
    "username": "janez",
    "age": 35,
    "height": 190,
    "weight": 80,
    "gender": "m",
    "activity_level": "moderate",
}
TEST_LOGGED_ITEM: dict[str, Any] = {
    "food_name": TEST_FOOD,
    "weight": 100.0,
}
RESPONSES_METHODS: list[str] = [
    responses.GET,
    responses.POST,
    responses.PUT,
    responses.DELETE,
    responses.PATCH,
    responses.HEAD,
    responses.OPTIONS,
]
load_dotenv()

def prepare_interception(
    client_food_item: FlaskClient,
    client_logged_item: FlaskClient,
    client_user_info: FlaskClient,
):
    for method in RESPONSES_METHODS:
        responses.add_callback(
            method=method,
            url=re.compile(r".*/api/v1/food_item/.*"),
            callback=callback_factory(client_food_item),
        )
        responses.add_callback(
            method=method,
            url=re.compile(r".*/api/v1/logged_item/.*"),
            callback=callback_factory(client_logged_item),
        )
        responses.add_callback(
            method=method,
            url=re.compile(r".*/api/v1/user_info/.*"),
            callback=callback_factory(client_user_info),
        )
        responses.add_callback(
            method=method,
            url=re.compile(r".*"),
            callback=callback_factory(None),
        )

@pytest.fixture(scope="function")
def database():
    # Close connection with prod DB
    disconnect_all()
    # Make connection to test DB
    client: MongoClient = connect(
        db=os.environ["MONGO_DB_TEST"],
        host=os.environ["MONGO_HOST"],
        port=int(os.environ["MONGO_PORT"]),
        username=os.environ["MONGO_USERNAME"],
        password=os.environ["MONGO_PASSWORD"],
        uuidRepresentation="standard",
    )
    db: Database = client.get_database(os.environ["MONGO_DB_TEST"])
    # Clear test DB
    for collection in db.list_collection_names():
        db.drop_collection(collection)
    # Run test
    yield db
    # Disconnect from DB
    disconnect_all()

@pytest.fixture
def client_food_item() -> FlaskClient:
    app_food_item.config["TESTING"] = True
    client: FlaskClient = app_food_item.test_client()
    return client

@pytest.fixture
def client_logged_item() -> FlaskClient:
    app_logged_item.config["TESTING"] = True
    client: FlaskClient = app_logged_item.test_client()
    return client

@pytest.fixture
def client_user_info() -> FlaskClient:
    app_user_info.config["TESTING"] = True
    client: FlaskClient = app_user_info.test_client()
    return client

@pytest.fixture
def clients() -> tuple[FlaskClient, FlaskClient, FlaskClient]:
    for app in [app_food_item, app_logged_item, app_user_info]:
        app.config["TESTING"] = True
    clients: tuple[FlaskClient, FlaskClient, FlaskClient] = (
        app_food_item.test_client(),
        app_logged_item.test_client(),
        app_user_info.test_client(),
    )
    # Add callbacks (intercept requests.*)
    prepare_interception(*clients)
    return clients

# https://github.com/getsentry/responses?tab=readme-ov-file#responses-as-a-pytest-fixture
def callback_factory(client: FlaskClient | None = None):
    def callback_flask(request: requests.models.PreparedRequest):
        if client is None:
            return (500, {}, None)
        resp: TestResponse = client.open(
            request.url,
            method=request.method,
            headers=request.headers,
            data=request.body,
        )
        return (resp.status_code, resp.headers, resp.data)
    def callback_requests(request: requests.models.PreparedRequest):
        responses.stop()
        session: requests.Session = requests.Session()
        resp: requests.Response = session.send(request)
        responses.start()
        return (resp.status_code, resp.headers, resp.content)
    return callback_requests if client is None else callback_flask

def create_food_item(client: FlaskClient, query: str) -> str:
    # Get response from API
    resp = client.get(f"/api/v1/food_item/{query}")
    assert resp.json is not None
    # Check if required keys are present
    required_keys: set[str] = {
        "calories",
        "carbohydrates",
        "cholesterol",
        "fat_saturated",
        "fat_total",
        "fiber",
        "id",
        "name",
        "potassium",
        "protein",
        "sodium",
        "sugar",
        "weight_g",
    }
    assert resp.json["food_item"]
    returned_keys: set[str] = set(resp.json["food_item"].keys())
    assert required_keys.issubset(returned_keys)
    # Check if returned name matches queried name
    assert resp.json["food_item"]["name"].lower() == query.lower()
    # Return id
    return resp.json["food_item"]["id"]

def create_user_info(client: FlaskClient, user: dict[str, Any]) -> str:
    # Get response from API
    resp = client.post(f"/api/v1/user_info/", json=user)
    assert resp.json is not None
    # Check if success message is present
    assert resp.json["message"]
    # Check if returned user is same as sent user
    for prop, value in user.items():
        assert resp.json["user_info"][prop] == value
    # Check if id is present
    assert resp.json["user_info"]["id"]
    # Return id
    return resp.json["user_info"]["id"]

def logged_item_add(
    client_food_item: FlaskClient,
    client_logged_item: FlaskClient,
    client_user_info: FlaskClient,
) -> tuple[str, str, str]:

    # Add food item
    food_item_id: str = create_food_item(client_food_item, TEST_FOOD)
    # Add user
    user_id: str = create_user_info(client_user_info, TEST_USER)

    # Add logged item (add food item to user)
    resp = client_logged_item.post(f"/api/v1/logged_item/user/{user_id}", json=TEST_LOGGED_ITEM)
    assert resp.json is not None
    # Check if success message is present
    assert resp.json["message"]
    # Check if returned item matches input data
    assert resp.json["logged_item"]["food_item_id"] == food_item_id
    assert resp.json["logged_item"]["user_id"] == user_id
    # Check for id presence
    assert resp.json["logged_item"]["id"]
    return (food_item_id, resp.json["logged_item"]["id"], user_id)

@responses.activate
def test_logged_item_add(
    clients: tuple[FlaskClient, FlaskClient, FlaskClient],
    database: Database,
):
    # Adds food item, user and logged item corresponding to those two
    logged_item_add(*clients)

def logged_item_get(
    clients: tuple[FlaskClient, FlaskClient, FlaskClient],
    food_item_id: str,
    logged_item_id: str,
    user_id: str,
):
    client_logged_item: FlaskClient = clients[1]
    resp = client_logged_item.get(f"/api/v1/logged_item/{logged_item_id}")
    assert resp.json is not None
    # Check for success message
    assert resp.json["message"]
    # Check if returned ids match
    assert resp.json["logged_item"]["food_item_id"] == food_item_id
    assert resp.json["logged_item"]["id"] == logged_item_id
    assert resp.json["logged_item"]["user_id"] == user_id

@responses.activate
def test_logged_item_get(
    clients: tuple[FlaskClient, FlaskClient, FlaskClient],
    database: Database,
):
    # Adds food item, user and logged item corresponding to those two
    food_item_id, logged_item_id, user_id = logged_item_add(*clients)

    # Get that same logged item and check that it matches the sent data
    logged_item_get(clients, food_item_id, logged_item_id, user_id)

@responses.activate
def test_logged_item_delete(
    clients: tuple[FlaskClient, FlaskClient, FlaskClient],
    database: Database,
):
    # Adds food item, user and logged item corresponding to those two
    food_item_id, logged_item_id, user_id = logged_item_add(*clients)

    # Get the logged item
    logged_item_get(clients, food_item_id, logged_item_id, user_id)

    # Delete item
    client_logged_item: FlaskClient = clients[1]
    resp = client_logged_item.delete(f"/api/v1/logged_item/{logged_item_id}")
    assert resp.json is not None
    # Check for success message
    assert resp.json["message"]

    # Delete item again (it shouldn't exist at this point)
    resp = client_logged_item.delete(f"/api/v1/logged_item/{logged_item_id}")
    assert resp.json is not None
    # Check for error message
    assert resp.json["error"]
    assert resp.status_code == 404

