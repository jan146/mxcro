from flask.testing import FlaskClient
from ..src.api.v1.api import app
import pytest

@pytest.fixture
def client() -> FlaskClient:
    app.config["TESTING"] = True
    client: FlaskClient = app.test_client()
    return client

def test_query(client: FlaskClient):
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

