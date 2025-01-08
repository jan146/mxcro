from typing import Any
from flask.testing import FlaskClient
from user_info.src.api.v1.api import app
import pytest
from pymongo.synchronous.database import Database
from pymongo.synchronous.mongo_client import MongoClient
from mongoengine import disconnect_all, connect
from dotenv import load_dotenv
import os
from unittest import mock

app.config["TESTING"] = True
TEST_USER: dict[str, Any] = {
    "username": "janez",
    "age": 35,
    "height": 190,
    "weight": 80,
    "gender": "m",
    "activity_level": "moderate",
}
load_dotenv()

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
def client() -> FlaskClient:
    client: FlaskClient = app.test_client()
    return client

def check_user_match(sent_user: dict[str, Any], response_data: dict[str, Any]):
    # Check if success message is present
    assert response_data["message"]
    # Check if returned user is same as sent user
    for prop, value in sent_user.items():
        assert response_data["user_info"][prop] == value

def test_user_creation(client: FlaskClient, database: Database):
    # Prepare new user
    new_user: dict[str, Any] = TEST_USER.copy()
    # Get response from API
    resp = client.post(f"/api/v1/user_info/", json=new_user)
    assert resp.json is not None
    # Check if response matches sent data
    check_user_match(sent_user=new_user, response_data=resp.json)

def test_user_creation_duplicates(client: FlaskClient, database: Database):
    # Prepare new user
    new_user: dict[str, Any] = TEST_USER.copy()
    # Create user
    resp = client.post(f"/api/v1/user_info/", json=new_user)
    assert resp.json is not None
    # Check if response matches sent data
    check_user_match(sent_user=new_user, response_data=resp.json)

    # Try to create user with identical username
    resp = client.post(f"/api/v1/user_info/", json=new_user)
    assert resp.json is not None
    # Check if there's an error when trying to recreate the same user
    assert resp.json["error"]
    assert 400 <= resp.status_code < 500

def test_user_get(client: FlaskClient, database: Database):
    # Prepare new user
    new_user: dict[str, Any] = TEST_USER.copy()
    # Create user
    resp = client.post(f"/api/v1/user_info/", json=new_user)
    assert resp.json is not None
    # Check if response matches sent data
    check_user_match(sent_user=new_user, response_data=resp.json)
    # Check for user id
    assert resp.json["user_info"]["id"]
    user_id: str = resp.json["user_info"]["id"]

    # Fetch the created user by id
    resp = client.get(f"/api/v1/user_info/id/{user_id}")
    assert resp.json is not None
    # Check if response matches sent data
    for prop, value in new_user.items():
        assert resp.json[prop] == value
    assert resp.json["id"] == user_id

    # Fetch the created user by username
    resp = client.get(f"/api/v1/user_info/username/{new_user['username']}")
    assert resp.json is not None
    # Check if response matches sent data
    for prop, value in new_user.items():
        assert resp.json[prop] == value
    assert resp.json["id"] == user_id

def test_user_deletion(client: FlaskClient, database: Database):
    # Prepare new user
    new_user: dict[str, Any] = TEST_USER.copy()
    # Create user
    resp = client.post(f"/api/v1/user_info/", json=new_user)
    assert resp.json is not None
    # Check if response matches sent data
    check_user_match(sent_user=new_user, response_data=resp.json)
    # Check for user id
    assert resp.json["user_info"]["id"]
    user_id: str = resp.json["user_info"]["id"]

    # Fetch the created user by id
    resp = client.get(f"/api/v1/user_info/id/{user_id}")
    assert resp.json is not None
    # Check if response matches sent data
    for prop, value in new_user.items():
        assert resp.json[prop] == value
    assert resp.json["id"] == user_id

    # Mocking the requests.delete to simulate deleting logged_item entities
    with mock.patch("requests.delete") as mock_delete:
        # Delete user
        # Simulate a successful deletion response from the logged_item service
        mock_delete.return_value.status_code = 200
        mock_delete.return_value.json.return_value = {"message": f"Successfully deleted logged item with id ..."}
        # Send the DELETE request to the user service
        resp = client.delete(f"/api/v1/user_info/id/{user_id}")
        assert resp.json is not None
        # Check that the response is successful
        assert resp.status_code == 200
        assert resp.json["message"]
        # Verify that the mock delete was called with the correct URL
        mock_delete.assert_called_once_with(f"{os.environ['BACKEND_URL']}/api/v1/logged_item/user/{user_id}")

        # Try to re-delete user (it should be non-existent at this point)
        resp = client.delete(f"/api/v1/user_info/id/{user_id}")
        assert resp.json is not None
        assert resp.json["error"]
        assert resp.status_code == 404

    # Try to fetch the non-existent user by id
    resp = client.get(f"/api/v1/user_info/id/{user_id}")
    assert resp.json is not None
    assert resp.json["error"]
    assert resp.status_code == 404

def test_daily_rda(client: FlaskClient, database: Database):
    # Prepare new user
    new_user: dict[str, Any] = TEST_USER.copy()
    # Create user
    resp = client.post(f"/api/v1/user_info/", json=new_user)
    assert resp.json is not None
    # Check if response matches sent data
    check_user_match(sent_user=new_user, response_data=resp.json)
    # Check for user id
    assert resp.json["user_info"]["id"]
    user_id: str = resp.json["user_info"]["id"]

    # Get user's daily RDA values
    resp = client.get(f"/api/v1/user_info/daily_rda/{user_id}")
    assert resp.json is not None
    # Check if required keys are present
    required_keys: set[str] = {
        "bmr",
        "tdee",
        "calories",
        "carbohydrates",
        "cholesterol",
        "fat_saturated",
        "fat_total",
        "fiber",
        "potassium",
        "protein",
        "sodium",
        "sugar",
    }
    returned_keys: set[str] = set(resp.json.keys())
    assert required_keys.issubset(returned_keys)
    # Sanity check returned values
    for key in required_keys:
        assert 0.0 < float(resp.json[key]) 

