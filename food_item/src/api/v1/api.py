import os
from flask import Flask, jsonify
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from mongoengine import connect
from dotenv import load_dotenv
from food_item.src.core.manage_food_item import get_nutrition_facts
from food_item.src.models.converters.food_item_converter import FoodItemConverter
from food_item.src.models.entities.food_item import FoodItem

load_dotenv()
connect(
    db=os.environ["MONGO_DB_NAME"],
    host=os.environ["MONGO_HOST"],
    port=int(os.environ["MONGO_PORT"]),
    username=os.environ["MONGO_USERNAME"],
    password=os.environ["MONGO_PASSWORD"],
)
app: Flask = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
@app.route("/api/v1", methods=["GET"])
def home():
    return "Hello, this is the root endpoint of food_item"

@app.route("/api/v1/food_item/<query>", methods=["GET"])
def food_item(query: str):
    result: FoodItem | tuple[int, str] = get_nutrition_facts(query)
    if isinstance(result, FoodItem):
        return jsonify({"food_item": FoodItemConverter.to_dict(result)}), 200
    return jsonify({"error": result[1]}), result[0]

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

