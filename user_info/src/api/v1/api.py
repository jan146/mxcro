import requests
import os
from typing import cast
from flask import Flask, jsonify, request
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from mongoengine import connect
from dotenv import load_dotenv
from user_info.src.core.user_info import create_user, get_user_info
from user_info.src.models.converters import user_info_converter
from user_info.src.models.converters.user_info_converter import UserInfoConverter
from user_info.src.models.entities.user_info import UserInfo

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
    return "Hello, this is the root endpoint of user_info"

@app.route("/user_info/id/<id>", methods=["GET", "POST", "OPTIONS"])
def user_info(id: str):
    match request.method.lower():
        case "options":
            return jsonify({}), 200
        case "get":
            user_info: UserInfo | None = get_user_info(id)
            if user_info:
                return jsonify(UserInfoConverter.to_dict(user_info)), 200
            else:
                return jsonify({"error": "User not found"}), 404
        case "post":
            data: dict[str, str] = cast(dict[str, str], request.json)
            try:
                user: UserInfo = create_user(data)
                return jsonify({"message": "User successfully created", "user_info": UserInfoConverter.to_dict(user)}), 200
            except Exception as e:
                return jsonify({"error": f"Failed to create user: {str(e)}"}), 400
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

