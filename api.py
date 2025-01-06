from flask import Flask
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
import os
import re
from food_item.src.api.v1.api import app as app_food_item
from user_info.src.api.v1.api import app as app_user_info
from logged_item.src.api.v1.api import app as app_logged_item

app: Flask = Flask(__name__)
CORS(app)

# Register routes from app_food_item
for rule in app_food_item.url_map.iter_rules():
    if rule.endpoint in ["home", "static"]:
        continue
    if rule.endpoint.startswith("swagger") or rule.endpoint.startswith("openapi"):
        rule.endpoint = f"food_item.{rule.endpoint}"
    app.add_url_rule(
        f"{rule}",
        endpoint=rule.endpoint,
        view_func=app_food_item.view_functions[re.sub(r"^food_item\.", r"", rule.endpoint)],
        methods=rule.methods,
    )

# Register routes from app_user_info
for rule in app_user_info.url_map.iter_rules():
    if rule.endpoint in ["home", "static"]:
        continue
    if rule.endpoint.startswith("swagger") or rule.endpoint.startswith("openapi"):
        rule.endpoint = f"user_info.{rule.endpoint}"
    app.add_url_rule(
        f"{rule}",
        endpoint=rule.endpoint,
        view_func=app_user_info.view_functions[re.sub(r"^user_info\.", r"", rule.endpoint)],
        methods=rule.methods,
    )

# Register routes from app_logged_item
for rule in app_logged_item.url_map.iter_rules():
    if rule.endpoint in ["home", "static"]:
        continue
    if rule.endpoint.startswith("swagger") or rule.endpoint.startswith("openapi"):
        rule.endpoint = f"logged_item.{rule.endpoint}"
    app.add_url_rule(
        f"{rule}",
        endpoint=rule.endpoint,
        view_func=app_logged_item.view_functions[re.sub(r"^logged_item\.", r"", rule.endpoint)],
        methods=rule.methods,
    )

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

