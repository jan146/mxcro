import requests
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from mongoengine import connect
from dotenv import load_dotenv
from typing import Any, cast
from logged_item.src.core.manage_logged_item import add_item_to_user, get_logged_items
from logged_item.src.models.converters.logged_item_converter import LoggedItemConverter
from logged_item.src.models.entities.logged_item import LoggedItem

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
def home():
    return "Hello, this is the root endpoint of logged_item"

@app.route("/logged_item/<user_id>", methods=["GET", "POST", "OPTIONS"])
def add_item(user_id: str):
    match request.method.lower():
        case "options":
            return jsonify({}), 200
        case "post":
            data: dict[str, str] = cast(dict[str, str], request.json)
            try:
                logged_item: LoggedItem = add_item_to_user(user_id, data)
                return jsonify({"message": "Successfully logged new item", "logged_item": LoggedItemConverter.to_dict(logged_item)}), 200
            except Exception as e:
                return jsonify({"error": f"Failed to log item: {str(e)}"}), 400
        case "get":
            try:
                logged_items: list[dict[str, Any]] = get_logged_items(user_id)
                return jsonify({"logged_items": logged_items}), 200
            except Exception as e:
                return jsonify({"error": f"Failed to get logged items: {str(e)}"}), 400
    return jsonify({"error": f"Method not supported: {request.method}"}), 405

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

