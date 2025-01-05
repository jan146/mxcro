# Mxcro
A simple microservice-based application used for logging and tracking personal nutrient intake.
The goal is to help the user make better decisions for maintaining a healthy and balanced diet.

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
- logged_item
- user_info

# How to run (local)

## Installation
```sh
git clone https://github.com/jan146/mxcro.git
cd mxcro
pip install -r requirements.txt
$EDITOR .env                                   # See section "Environment setup"
python -m [microservice].src.api.v1.api        # [microservice] is one of the three microservices
```

## Environment setup

Required variables:
- FLASK_DEBUG (set to "false" to disable Flask's debug mode, e.g. `False`)
- FLASK_HOST (set host that Flask server should listen on, e.g. `0.0.0.0`)
- FLASK_PORT (set port that Flask server should listen on, e.g. `5000`)
- ENVIRONMENT (set to "production" to use WSGIServer, e.g. `production`)
- MONGO_HOST (host that MongoDB is running on, e.g. `localhost`)
- MONGO_PORT (the port that MongoDB is listening on, e.g. `27017`)
- MONGO_DB_NAME (name of database in MongoDB instance, e.g. `mxcro`)
- MONGO_USERNAME (set to MongoDB, e.g. `user`)
- SERVERLESS_NAMESPACE_URL (the url of the namespace with required serverless functions, e.g. `https://faas-fra1-afec6ce7.doserverless.co/api/v1/namespaces/fn-1fe3ffab-d547-44e2-8b38-2158e175bae3`, see section "Serverless")
- BACKEND_URL (the url that microservices will use to access each other's APIs, e.g. `http://localhost:5000`)

Required variables (secrets):
- CALORIE_NINJAS_API_KEY
- MONGO_PASSWORD
- SERVERLESS_AUTH

## Serverless
The application uses serverless functions for calculating daily RDA values.
The necessary functions (modules) are available at `serverless/*`.

# How to run (Kubernetes)

## ConfigMap
Configuration options may be changed by editing `k8s/configmap.yaml`.
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

## Adding Nginx ingress controller ([source](https://www.digitalocean.com/community/developer-center/how-to-install-and-configure-ingress-controller-using-nginx))
```bash
# Find chart in repository
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update ingress-nginx
helm search repo ingress-nginx

# Install the chart
helm install ingress-nginx ingress-nginx/ingress-nginx --version "4.1.3" \
  --namespace ingress-nginx \
  --create-namespace \
  -f "k8s/nginx-values-v4.1.3.yaml"
```
