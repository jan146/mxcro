from flask import Flask
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
import os
from food_item.src.api.v1.api import app as app_food_item
from user_info.src.api.v1.api import app as app_user_info
from logged_item.src.api.v1.api import app as app_logged_item

app: Flask = Flask(__name__)
CORS(app)

# Register routes from app_food_item
for rule in app_food_item.url_map.iter_rules():
    if rule.endpoint in ["home", "static"]:
        continue
    app.add_url_rule(f"{rule}", endpoint=rule.endpoint, view_func=app_food_item.view_functions[rule.endpoint])

# Register routes from app_user_info
for rule in app_user_info.url_map.iter_rules():
    if rule.endpoint in ["home", "static"]:
        continue
    app.add_url_rule(f"{rule}", endpoint=rule.endpoint, view_func=app_user_info.view_functions[rule.endpoint])

# Register routes from app_logged_item
for rule in app_logged_item.url_map.iter_rules():
    if rule.endpoint in ["home", "static"]:
        continue
    app.add_url_rule(f"{rule}", endpoint=rule.endpoint, view_func=app_logged_item.view_functions[rule.endpoint])

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
    app.run(host='0.0.0.0', port=5000)
