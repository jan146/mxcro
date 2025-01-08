from flask.testing import FlaskClient
from ..src.api.v1.api import app
import pytest
from pymongo.synchronous.database import Database
from pymongo.synchronous.mongo_client import MongoClient
from mongoengine import disconnect_all, connect
from dotenv import load_dotenv
import os

app.config["TESTING"] = True
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

def test_query(client: FlaskClient, database: Database):
    # Prepare request
    query: str = "apple"
    # Get response from API
    resp = client.get(f"/api/v1/food_item/{query}")
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
    returned_keys: set[str] = set(resp.json["food_item"].keys())
    assert required_keys.issubset(returned_keys)
    # Check if returned name matches queried name
    assert resp.json["food_item"]["name"] == query

