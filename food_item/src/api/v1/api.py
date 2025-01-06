import os
from flask import jsonify
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from mongoengine import connect, get_connection
from dotenv import load_dotenv
from food_item.src.core.manage_food_item import check_calorie_ninjas_api_status, get_nutrition_facts
from food_item.src.models.converters.food_item_converter import FoodItemConverter
from food_item.src.models.entities.food_item import FoodItem
from pydantic import BaseModel, Field
from flask_openapi3.openapi import OpenAPI
from flask_openapi3.models.info import Info
from flask_openapi3.models.tag import Tag

load_dotenv()
connect(
    db=os.environ["MONGO_DB_NAME"],
    host=os.environ["MONGO_HOST"],
    port=int(os.environ["MONGO_PORT"]),
    username=os.environ["MONGO_USERNAME"],
    password=os.environ["MONGO_PASSWORD"],
)
info: Info = Info(title="Food item microservice API", version="1.0.0")
app: OpenAPI = OpenAPI(__name__, info=info, doc_prefix="/food_item/openapi")
CORS(app)

class QueryPath(BaseModel):
    query: str = Field(..., description="Query (food name)")

class FoodItemResponse(BaseModel):
    id: str = Field("677ab2484ec48c1511323964", description="ID of specified food item")
    name: str = Field("banana", description="Name of the queried food item")
    weight_g: float = Field(100.0, description="Serving size (returned nutrient values are based on this value)")
    calories: float = Field(89.4, description="Number of calories")
    fat_total: float = Field(0.3, description="Total amout of fats in grams")
    fat_saturated: float = Field(0.1, description="Total amout of saturated saturated fats in grams")
    carbohydrates: float = Field(23.2, description="Total amout of carbohydrates in grams")
    fiber: float = Field(2.6, description="Total amout of fiber in grams")
    sugar: float = Field(12.3, description="Total amout of sugar in grams")
    protein: float = Field(1.1, description="Total amout of protein in grams")
    cholesterol: float = Field(0.0, description="Total amout of cholesterol in milligrams")
    potassium: float = Field(22.0, description="Total amout of potassium in milligrams")
    sodium: float = Field(1.0, description="Total amout of sodium in milligrams")

class QueryResponse(BaseModel):
    food_item: FoodItemResponse

class QueryResponseError(BaseModel):
    error: str = Field("HTTPSConnectionPool(host='api.calorieninjas.com', port=443): Max retries exceeded with url: ...")

class HomeResponse(BaseModel):
    message: str = Field("Hello, this is the root endpoint of food_item", description="Greeting")

class LivenessResponse(BaseModel):
    message: str = Field("Liveness probe successful", description="Success message")

class ReadinessResponseOk(BaseModel):
    message: str = Field("Readiness probe successful", description="Success message")

class ReadinessResponseDatabase(BaseModel):
    error: str = Field("Database not available: ...", description="Error message")

class ReadinessResponseAPI(BaseModel):
    error: str = Field("Timeout reached when reaching Calorie Ninjas API ...", description="Error message")

@app.get(
    "/api/v1/",
    responses={
        200: HomeResponse,
    },
)
def home():
    return jsonify({"message": "Hello, this is the root endpoint of food_item"}), 200

@app.get(
    "/api/v1/food_item/<string:query>",
    tags=[Tag(name="Query", description="Return nutrition facts about the given food")],
    responses={
        200: QueryResponse,
        204: None,
        500: QueryResponseError,
    }
)
def food_item(path: QueryPath):
    result: FoodItem | tuple[int, str] = get_nutrition_facts(path.query)
    if isinstance(result, FoodItem):
        return jsonify({"food_item": FoodItemConverter.to_dict(result)}), 200
    return jsonify({"error": result[1]}), 500

@app.get(
    "/api/v1/food_item/health/live",
    responses={
        200: LivenessResponse,
    }
)
def food_item_liveness_probe():
    return jsonify({"message": "Liveness probe successful"}), 200

@app.get(
    "/api/v1/food_item/health/ready",
    responses={
        200: ReadinessResponseOk,
        503: ReadinessResponseDatabase,
        504: ReadinessResponseAPI,
    },
)
def food_item_readiness_probe():
    # Check database availability
    try:
        get_connection().server_info()
    except Exception as e:
        return jsonify({"error": f"Database not available: {str(e)}"}), 503
    # Check calorie ninjas API
    try:
        check_calorie_ninjas_api_status()
    except Exception as e:
        return jsonify({"error": str(e)}), 504
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

