import os
from flask import jsonify, request
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from mongoengine import connect, get_connection
from dotenv import load_dotenv
from typing import Any, cast
from logged_item.src.core.manage_logged_item import add_item_to_user, delete_logged_item, delete_logged_items_for_user, get_logged_item, get_logged_items
from logged_item.src.models.converters.logged_item_converter import LoggedItemConverter
from logged_item.src.models.entities.logged_item import LoggedItem
import datetime
import time
from flask_openapi3.openapi import OpenAPI
from flask_openapi3.models.info import Info
from flask_openapi3.models.tag import Tag
from pydantic import BaseModel, Field

DATE_FORMAT: str = "%d/%m/%Y"

load_dotenv()
connect(
    db=os.environ["MONGO_DB_NAME"],
    host=os.environ["MONGO_HOST"],
    port=int(os.environ["MONGO_PORT"]),
    username=os.environ["MONGO_USERNAME"],
    password=os.environ["MONGO_PASSWORD"],
    uuidRepresentation="standard",
)
info: Info = Info(title="Logged item microservice API", version="1.0.0")
app: OpenAPI = OpenAPI(__name__, info=info, doc_prefix="/logged_item/openapi")
CORS(app)

TAG_ITEM: Tag = Tag(name="Logged item", description="Manage logged items")
TAG_USER: Tag = Tag(name="User", description="Manage logged items for specific user")
TAG_HEALTH: Tag = Tag(name="Health", description="Health checking probes")

class HomeResponse(BaseModel):
    message: str = Field("Hello, this is the root endpoint of logged_item", description="Greeting")

class LivenessResponse(BaseModel):
    message: str = Field("Liveness probe successful", description="Success message")

class ReadinessResponseOk(BaseModel):
    message: str = Field("Readiness probe successful", description="Success message")

class ReadinessResponseDatabase(BaseModel):
    error: str = Field("Database not available: ...", description="Error message")

class LoggedItemPydantic(BaseModel):
    id: str = Field("67793f2c4917570eb704a0eb")
    timestamp: float = Field(1736509328.4)
    quantity: float = Field(100.0)
    user_id: str = Field("67793ecb4917570eb704a0e9")
    food_item_id: str = Field("67793f2c4917570eb704a0ea")

class GetItemResponse(BaseModel):
    message: str = Field("Successfully found logged item with id ...", description="Success message")
    logged_item: LoggedItemPydantic

class ItemNotFoundResponse(BaseModel):
    message: str = Field("Item not found", description="Error message")

class DeleteItemResponse(BaseModel):
    message: str = Field("Successfully deleted logged item with id=...", description="Success message")

class LoggedItemWithNutrientsPydantic(BaseModel):
    id: str = Field("677c01f8672293a1c0d3ba5e", description="ID of specified food item")
    name: str = Field("cheese", description="Name of the queried food item")
    weight_g: float = Field(100.0, description="Serving size (returned nutrient values are based on this value)")
    calories: float = Field(393.9, description="Number of calories")
    fat_total: float = Field(33.0, description="Total amout of fats in grams")
    fat_saturated: float = Field(18.9, description="Total amout of saturated saturated fats in grams")
    carbohydrates: float = Field(3.2, description="Total amout of carbohydrates in grams")
    fiber: float = Field(0.0, description="Total amout of fiber in grams")
    sugar: float = Field(0.5, description="Total amout of sugar in grams")
    protein: float = Field(22.7, description="Total amout of protein in grams")
    cholesterol: float = Field(100.0, description="Total amout of cholesterol in milligrams")
    potassium: float = Field(459.0, description="Total amout of potassium in milligrams")
    sodium: float = Field(661.0, description="Total amout of sodium in milligrams")

class GetUserItemsResponse(BaseModel):
    logged_items: list[LoggedItemWithNutrientsPydantic]

class GetUserItemsResponseError(BaseModel):
    error: str = Field("Failed to get logged items: ...", description="Error message")

class AddItemToUserResponse(BaseModel):
    message: str = Field("Successfully logged new item", description="Success message")
    logged_item: LoggedItemWithNutrientsPydantic

class AddItemToUserResponseError(BaseModel):
    error: str = Field("Failed to log item: ...", description="Error message")

class DeleteItemsFromUser(BaseModel):
    message: str = Field("Successfully deleted logged items for user with id ...", description="Success message")

class DeleteItemsFromUserError(BaseModel):
    error: str = Field("Failed to delete user's items: ...", description="Error message")

class ManageItemPath(BaseModel):
    id: str = Field(..., description="Id of logged item entity")

class ManageUserPath(BaseModel):
    user_id: str = Field(..., description="Id of user")

class LoggedItemBody(BaseModel):
    food_name: str = Field("Apple", description="Name of the food")
    weight: float = Field(100.0, description="Weight in grams")

@app.get(
    "/api/v1/",
    responses={
        200: HomeResponse,
    },
)
def home():
    return jsonify({"message": "Hello, this is the root endpoint of logged_item"}), 200

@app.get(
    "/api/v1/logged_item/<string:id>",
    tags=[TAG_ITEM],
    summary="Get a specific logged item by id",
    responses={
        200: GetItemResponse,
        404: ItemNotFoundResponse,
    },
)
def get_item(path: ManageItemPath):
    logged_item: LoggedItem | None = get_logged_item(path.id)
    if logged_item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify({"message": f"Successfully found logged item with id {path.id}", "logged_item": LoggedItemConverter.to_dict(logged_item)}), 200

@app.delete(
    "/api/v1/logged_item/<string:id>",
    tags=[TAG_ITEM],
    summary="Delete a single logged item",
    responses={
        200: DeleteItemResponse,
        404: ItemNotFoundResponse,
    },
)
def delete_item(path: ManageItemPath):
    logged_item: LoggedItem | None = get_logged_item(path.id)
    if logged_item is None:
        return jsonify({"error": "Item not found"}), 404
    delete_logged_item(path.id)
    return jsonify({"message": f"Successfully deleted logged item with id {path.id}"}), 200

@app.get(
    "/api/v1/logged_item/user/<string:user_id>",
    tags=[TAG_USER],
    summary="Get all of user's logged items",
    responses={
        200: GetUserItemsResponse,
        400: GetUserItemsResponseError,
    },
)
def get_user_logged_items(path: ManageUserPath):
    from_date: datetime.date = datetime.date.fromtimestamp(0)
    to_date: datetime.date = datetime.date.fromtimestamp(time.time())
    from_str: str | None = request.args.get("from")
    to_str: str | None = request.args.get("to")
    if from_str:
        from_date = datetime.datetime.strptime(from_str, DATE_FORMAT).date()
    if to_str:
        to_date = datetime.datetime.strptime(to_str, DATE_FORMAT).date()
    try:
        logged_items: list[dict[str, Any]] = get_logged_items(path.user_id, from_date, to_date)
        return jsonify({"logged_items": logged_items}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get logged items: {str(e)}"}), 400

@app.post(
    "/api/v1/logged_item/user/<string:user_id>",
    tags=[TAG_USER],
    summary="Add new item to user",
    responses={
        200: AddItemToUserResponse,
        400: AddItemToUserResponseError,
    },
)
def add_logged_item_to_user(path: ManageUserPath, body: LoggedItemBody):
    data: dict[str, str] = cast(dict[str, str], body.model_dump())
    date_str: str | None = request.args.get("date")
    date: datetime.date = datetime.date.today()
    if date_str:
        date = datetime.datetime.strptime(date_str, DATE_FORMAT).date()
    try:
        logged_item: LoggedItem | None = add_item_to_user(path.user_id, date, data)
        if logged_item is None:
            return jsonify({"message": f"The queried food \"{data['food_name']}\" is unfortunately not available"}), 200
        return jsonify({"message": "Successfully logged new item", "logged_item": LoggedItemConverter.to_dict(logged_item)}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to log item: {str(e)}"}), 400

@app.delete(
    "/api/v1/logged_item/user/<user_id>",
    tags=[TAG_USER],
    summary="Delete all user's logged items",
    responses={
        200: DeleteItemsFromUser,
        400: DeleteItemsFromUserError,
    },
)
def delete_logged_item_from_user(path: ManageUserPath):
    try:
        delete_logged_items_for_user(path.user_id)
    except Exception as e:
        return jsonify({"error": f"Failed to delete user's items: {str(e)}"}), 400
    return jsonify({"message": f"Successfully deleted logged items for user with id {path.user_id}"}), 200

@app.get(
    "/api/v1/logged_item/health/live",
    tags=[TAG_HEALTH],
    summary="Liveness probe",
    responses={
        200: LivenessResponse,
    }
)
def logged_item_liveness_probe():
    return jsonify({"message": "Liveness probe successful"}), 200

@app.get(
    "/api/v1/logged_item/health/ready",
    tags=[TAG_HEALTH],
    summary="Readiness probe",
    responses={
        200: ReadinessResponseOk,
        503: ReadinessResponseDatabase,
    },
)
def logged_item_readiness_probe():
    # Check database availability
    try:
        get_connection().server_info()
    except Exception as e:
        return jsonify({"error": f"Database not available: {str(e)}"}), 503
    return jsonify({"message": "Readiness probe successful"}), 200

if __name__ == "__main__":
    environment: str = os.environ.get("ENVIRONMENT", "development").lower()
    debug: bool = (os.environ.get("FLASK_DEBUG", "True").lower() != "false")
    host: str = os.environ.get("FLASK_HOST", "0.0.0.0")
    port: int = int(os.environ.get("FLASK_PORT", 5000))
    if environment in ["prod", "production"]:
        http_server = WSGIServer((host, port), app)
        http_server.serve_forever()
    else:
        app.run(debug=debug, host=host, port=port)

