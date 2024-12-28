import requests
import os
from flask import Flask, jsonify
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from mongoengine import connect
from dotenv import load_dotenv
from user_info.src.core.user_info import get_user_info
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

@app.route("/user_info/<id>", methods=["GET"])
def user_info(id: str):
    user_info: UserInfo | None = get_user_info(id)
    if user_info:
        return jsonify(UserInfoConverter.to_dict(user_info)), 200
    else:
        return jsonify({"error": "User not found"}), 404

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

