import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from mongoengine import connect
from dotenv import load_dotenv
from typing import Any, cast
from logged_item.src.core.manage_logged_item import add_item_to_user, delete_logged_item, get_logged_items
from logged_item.src.models.converters.logged_item_converter import LoggedItemConverter
from logged_item.src.models.entities.logged_item import LoggedItem
import datetime
import time

DATE_FORMAT: str = "%d/%m/%Y"

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

@app.route("/logged_item/<id>", methods=["GET", "POST", "OPTIONS", "DELETE"])
def manage_item(id: str):
    match request.method.lower():
        case "options":
            return jsonify({}), 200
        case "post":
            data: dict[str, str] = cast(dict[str, str], request.json)
            date_str: str | None = request.args.get("date")
            date: datetime.date = datetime.date.today()
            if date_str:
                date = datetime.datetime.strptime(date_str, DATE_FORMAT).date()
            try:
                logged_item: LoggedItem = add_item_to_user(id, date, data)
                return jsonify({"message": "Successfully logged new item", "logged_item": LoggedItemConverter.to_dict(logged_item)}), 200
            except Exception as e:
                return jsonify({"error": f"Failed to log item: {str(e)}"}), 400
        case "get":
            from_date: datetime.date = datetime.date.fromtimestamp(0)
            to_date: datetime.date = datetime.date.fromtimestamp(time.time())
            from_str: str | None = request.args.get("from")
            to_str: str | None = request.args.get("to")
            if from_str:
                from_date = datetime.datetime.strptime(from_str, DATE_FORMAT).date()
            if to_str:
                to_date = datetime.datetime.strptime(to_str, DATE_FORMAT).date()
            try:
                logged_items: list[dict[str, Any]] = get_logged_items(id, from_date, to_date)
                return jsonify({"logged_items": logged_items}), 200
            except Exception as e:
                return jsonify({"error": f"Failed to get logged items: {str(e)}"}), 400
        case "delete":
            delete_logged_item(id)
            return jsonify({"message": f"Successfully deleted logged item with {id=}"}), 200
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

