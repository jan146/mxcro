# Mxcro
A simple microservice-based application used for logging and tracking personal nutrient intake.
The goal is to help the user make better decisions for maintaining a healthy and balanced diet.

| Technology    | Implementation |
| ------------- | -------------- |
| Backend | Python (Flask) |
| Frontend | Vue.js |
| Database | MongoDB |
| ODM | MongoEngine |

## How to run
TODO

### Adding Nginx ingress controller ([source](https://www.digitalocean.com/community/developer-center/how-to-install-and-configure-ingress-controller-using-nginx))
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
