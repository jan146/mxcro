import os
from typing import Any, cast
from flask import Response, jsonify, request
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from mongoengine import connect, get_connection
from dotenv import load_dotenv
from user_info.src.core.daily_rda import get_daily_rda
from user_info.src.core.manage_user_info import check_serverless, create_user, delete_user, get_user_info, get_user_info_by_username
from user_info.src.models.converters.user_info_converter import UserInfoConverter
from user_info.src.models.entities.user_info import UserInfo
from flask_openapi3.openapi import OpenAPI
from flask_openapi3.models.info import Info
from flask_openapi3.models.tag import Tag
from pydantic import BaseModel, Field
from prometheus_client import make_wsgi_app, Counter, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import time

load_dotenv()
connect(
    db=os.environ["MONGO_DB_NAME"],
    host=os.environ["MONGO_HOST"],
    port=int(os.environ["MONGO_PORT"]),
    username=os.environ["MONGO_USERNAME"],
    password=os.environ["MONGO_PASSWORD"],
    uuidRepresentation="standard",
)
info: Info = Info(title="User info microservice API", version="1.0.0")
app: OpenAPI = OpenAPI(__name__, info=info, doc_prefix="/user_info/openapi")
CORS(app)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    "/user_info/metrics": make_wsgi_app()
})

TAG_USER: Tag = Tag(name="User", description="Manage user")
TAG_RDA: Tag = Tag(name="RDA", description="Daily RDA (recommended dietary allowance)")
TAG_HEALTH: Tag = Tag(name="Health", description="Health checking probes")

class HomeResponse(BaseModel):
    message: str = Field("Hello, this is the root endpoint of logged_item", description="Greeting")

class UserInfoPydantic(BaseModel):
    id: str = Field("6770566535c6d727a838e434")
    username: str = Field("janez")
    age: int = Field(30)
    height: float = Field(175.0)
    weight: float = Field(70.0)
    gender: str = Field("m")
    activity_level: str = Field("moderate")

class UserCreatedResponse(BaseModel):
    message: str = Field("User successfully created", description="Success message")
    user_info: UserInfoPydantic

class UserCreatedResponseError(BaseModel):
    error: str = Field("Failed to create user: ...", description="Error message")

class UserNotFoundResponse(BaseModel):
    error: str = Field("User not found", description="Error message")

class DeleteUserResponse(BaseModel):
    message: str = Field("User successfully deleted", description="Success message")
    user_info: UserInfoPydantic

class DailyRdaPydantic(BaseModel):
    bmr: float = Field(1648.75, description="Basal metabolic rate")
    tdee: float = Field(2555.5625, description="Total daily energy expenditure")
    calories: float = Field(2555.5625, description="Daily calorie allowance")
    fat_total: int = Field(85, description="Daily total fats allowance, in grams")
    fat_saturated: int = Field(28, description="Daily saturated fats allowance, in grams")
    carbohydrates: int = Field(287, description="Daily carbohydrates allowance, in grams")
    fiber: int = Field(35, description="Daily fiber allowance, in grams")
    sugar: int = Field(38, description="Daily sugar allowance, in grams")
    protein: int = Field(159, description="Daily protein allowance, in grams")
    potassium: int = Field(3400, description="Daily potassium allowance, in milligrams")
    sodium: int = Field(2300, description="Daily sodium allowance, in milligrams")
    cholesterol: int = Field(300, description="Daily cholesterol allowance, in milligrams")

class LivenessResponse(BaseModel):
    message: str = Field("Liveness probe successful", description="Success message")

class ReadinessResponseOk(BaseModel):
    message: str = Field("Readiness probe successful", description="Success message")

class ReadinessResponseDatabase(BaseModel):
    error: str = Field("Database not available: ...", description="Error message")

class ReadinessResponseServerless(BaseModel):
    error: str = Field("Error while executing serverless function: ...", description="Error message")

class UserIdPath(BaseModel):
    id: str = Field(..., description="Id of user")

class UsernamePath(BaseModel):
    username: str = Field(..., description="User's unique username")

REQ_COUNT: Counter = Counter(
    "user_info_req_count",
    "Microservice user_info Request Count",
    ["method", "endpoint", "http_status"],
)
REQ_LATENCY: Histogram = Histogram(
    "user_info_req_latency",
    "Microservice user_info Request Latency",
    ["method", "endpoint"],
)

@app.get(
    "/api/v1/",
    responses={
        200: HomeResponse,
    },
)
def home():
    return jsonify({"message": "Hello, this is the root endpoint of user_info"}), 200

@app.post(
    "/api/v1/user_info/",
    tags=[TAG_USER],
    summary="Create new user",
    responses={
        200: UserCreatedResponse,
        400: UserCreatedResponseError,
    },
)
def create_user_info(body: UserInfoPydantic):
    if request.method.lower() == "options":     # For some reason, the content-type isn't set to application/json for the OPTIONS request
        return jsonify({}), 200
    time_start: float = time.time()
    data: dict[str, str] = cast(dict[str, str], body.model_dump())
    response: tuple[Response, int] = jsonify({}), 0
    try:
        if "id" in data:
            del data["id"]
        user: UserInfo = create_user(data)
        response = jsonify({"message": "User successfully created", "user_info": UserInfoConverter.to_dict(user)}), 200
    except Exception as e:
        response = jsonify({"error": f"Failed to create user: {str(e)}"}), 400
    REQ_COUNT.labels("POST", "/api/v1/user_info/", response[1]).inc()
    REQ_LATENCY.labels("POST", "/api/v1/user_info/").observe(time.time() - time_start)
    return response

@app.get(
    "/api/v1/user_info/id/<string:id>",
    tags=[TAG_USER],
    summary="Get user by id",
    responses={
        200: UserInfoPydantic,
        404: UserNotFoundResponse,
    },
)
def get_user(path: UserIdPath):
    time_start: float = time.time()
    user_info: UserInfo | None = get_user_info(path.id)
    response: tuple[Response, int] = jsonify({}), 0
    if user_info is None:
        response = jsonify({"error": "User not found"}), 404
    else:
        response = jsonify(UserInfoConverter.to_dict(user_info)), 200
    REQ_COUNT.labels("GET", "/api/v1/user_info/id/<string:id>", response[1]).inc()
    REQ_LATENCY.labels("GET", "/api/v1/user_info/id/<string:id>").observe(time.time() - time_start)
    return response

@app.delete(
    "/api/v1/user_info/id/<string:id>",
    tags=[TAG_USER],
    summary="Delete user by id",
    responses={
        200: DeleteUserResponse,
        404: UserNotFoundResponse,
    },
)
def delete_user_info(path: UserIdPath):
    time_start: float = time.time()
    user_info: UserInfo | None = get_user_info(path.id)
    response: tuple[Response, int] = jsonify({}), 0
    if user_info is None:
        response = jsonify({"error": "User not found"}), 404
    else:
        user_dict: dict[str, Any] = UserInfoConverter.to_dict(user_info)
        delete_user(user_info)
        response = jsonify({"message": "User successfully deleted", "user_info": user_dict}), 200
    REQ_COUNT.labels("DELETE", "/api/v1/user_info/id/<string:id>", response[1]).inc()
    REQ_LATENCY.labels("DELETE", "/api/v1/user_info/id/<string:id>").observe(time.time() - time_start)
    return response

@app.get(
    "/api/v1/user_info/username/<string:username>",
    tags=[TAG_USER],
    summary="Get user by unique username",
    responses={
        200: UserInfoPydantic,
        404: UserNotFoundResponse,
    },
)
def user_info_by_username(path: UsernamePath):
    time_start: float = time.time()
    user_info: UserInfo | None = get_user_info_by_username(path.username)
    response: tuple[Response, int] = jsonify({}), 0
    if user_info:
        response = jsonify(UserInfoConverter.to_dict(user_info)), 200
    else:
        response = jsonify({"error": "User not found"}), 404
    REQ_COUNT.labels("GET", "/api/v1/user_info/username/<string:username>", response[1]).inc()
    REQ_LATENCY.labels("GET", "/api/v1/user_info/username/<string:username>").observe(time.time() - time_start)
    return response

@app.get(
    "/api/v1/user_info/daily_rda/<string:id>",
    tags=[TAG_RDA],
    summary="Get user's daily RDA values",
    responses={
        200: DailyRdaPydantic,
        404: UserNotFoundResponse,
    },
)
def daily_rda_for_user(path: UserIdPath):
    time_start: float = time.time()
    user_info: UserInfo | None = get_user_info(path.id)
    response: tuple[Response, int] = jsonify({}), 0
    if user_info is None:
        response = jsonify({"error": "User not found"}), 404
    else:
        daily_rda: dict[str, Any] = get_daily_rda(user_info)
        response = jsonify(daily_rda), 200
    REQ_COUNT.labels("GET", "/api/v1/user_info/daily_rda/<string:id>", response[1]).inc()
    REQ_LATENCY.labels("GET", "/api/v1/user_info/daily_rda/<string:id>").observe(time.time() - time_start)
    return response

@app.get(
    "/api/v1/user_info/health/live",
    tags=[TAG_HEALTH],
    summary="Liveness probe",
    responses={
        200: LivenessResponse,
    }
)
def user_info_liveness_probe():
    return jsonify({"message": "Liveness probe successful"}), 200

@app.get(
    "/api/v1/user_info/health/ready",
    tags=[TAG_HEALTH],
    summary="Readiness probe",
    responses={
        200: ReadinessResponseOk,
        503: ReadinessResponseDatabase,
        504: ReadinessResponseServerless,
    },
)
def user_info_readiness_probe():
    # Check database availability
    try:
        get_connection().server_info()
    except Exception as e:
        return jsonify({"error": f"Database not available: {str(e)}"}), 503
    # Check serverless functions availability
    try:
        check_serverless()
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

