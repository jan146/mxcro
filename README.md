# Mxcro
A simple microservice-based application used for logging and tracking personal nutrient intake.
The goal is to help the user make better decisions for maintaining a healthy and balanced diet.
Frontend is available [here](https://github.com/jan146/mxcro-frontend).

| Technology    | Implementation |
| ------------- | -------------- |
| Backend | Python (Flask) |
| Frontend | Vue.js, TypeScript, Bun |
| Database | MongoDB |
| ODM | MongoEngine |
| Container orchestration | Kubernetes |

## Structure

The application consists of three microservices:
- food_item
  - Manages food item entities
  - Communicates with external API ([Calorie Ninjas](https://calorieninjas.com/api))
- logged_item
  - Manages users' invidividually logged items/meals.
  - Acts as a sort of "bridge entity" between food_item and user_info
- user_info
  - Manages users' personal information
  - Uses serverless functions to calculate a person's daily RDA (reccomended dietary allowance)

# How to run (local)

## Installation
```sh
git clone https://github.com/jan146/mxcro.git
cd mxcro
pip install -r requirements.txt
$EDITOR .env                                   # See section "Environment setup"
python -m [microservice].src.api.v1.api        # [microservice] must be one of the three microservices
```
For development/debugging, you can also use the combined API:
```sh
python api.py
```

## Environment setup

Configuration is managed through environment variables.

Required variables:
- FLASK_DEBUG (set to "false" to disable Flask's debug mode, e.g. `False`)
- FLASK_HOST (set host that Flask server should listen on, e.g. `0.0.0.0`)
- FLASK_PORT (set port that Flask server should listen on, e.g. `5000`)
- ENVIRONMENT (set to "production" to use WSGIServer, e.g. `production`)
- MONGO_HOST (host that MongoDB is running on, e.g. `localhost`)
- MONGO_PORT (the port that MongoDB is listening on, e.g. `27017`)
- MONGO_DB_NAME (name of database in MongoDB instance, e.g. `mxcro`)
- MONGO_DB_TEST (name of database for testing in MongoDB instance, e.g. `mxcro-text`)
- MONGO_USERNAME (set to MongoDB, e.g. `user`)
- SERVERLESS_NAMESPACE_URL (the url of the namespace with required serverless functions, e.g. `https://faas-fra1-13b1c273.doserverless.co/api/v1/namespaces/fn-5fd4fbe1-16f6-7fdc-7238-6528c09a8ec4`, see section "Serverless")
- BACKEND_URL (the url that microservices will use to access each other's APIs, e.g. `http://localhost:5000`)

Required variables (secrets):
- CALORIE_NINJAS_API_KEY
- MONGO_PASSWORD
- SERVERLESS_AUTH

## Serverless
The application uses serverless functions for calculating daily RDA values.
The necessary functions (modules) are available at `serverless/*`.

# How to run (Kubernetes)

## Environment variables
Configuration options may be changed by editing `k8s/helm-mxcro-shared/templates/configmap.yaml`.
For descriptions, see required variables under "Environment setup" subsection of the "How to run (local)" section.

## Secrets
List of secrets can be found under "Environment setup" subsection of the "How to run (local)" section.
Secrets can be added using `kubectl` tool like so:
```sh
kubectl create secret generic mxcro-secrets \
  --from-literal=CALORIE_NINJAS_API_KEY="paste-calorie-ninjas-api-key-here" \
  --from-literal=SERVERLESS_AUTH="paste-serverless-auth-here" \
  --from-literal=MONGO_PASSWORD="paste-mongo-password-here"
```

## Adding deployments & services using helm
```sh
# Satisfy dependencies (only for mxcro-shared chart (which is only ingress-nginx))
helm dependency build k8s/helm-mxcro-shared

# Install mxcro-shared chart
helm install mxcro-shared k8s/helm-mxcro-shared

# Add the k8s ojbects for food_item microservice
helm install mxcro-food-item food_item/helm-mxcro-food-item        # Optionally add -f food_item/helm-mxcro-food-item/values.production.yaml
# Add the k8s ojbects for logged_item microservice
helm install mxcro-logged-item logged_item/helm-mxcro-logged-item  # Optionally add -f logged_item/helm-mxcro-logged-item/values.production.yaml
# Add the k8s ojbects for user_info microservice
helm install mxcro-user-info user_info/helm-mxcro-user-info        # Optionally add -f user_info/helm-mxcro-user-info/values.production.yaml
```
