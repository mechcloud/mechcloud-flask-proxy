# Flask Proxy Server
A simple Python based proxy server built with Flask, supporting CORS and TLS. It routes requests to configured backend services based on URL prefixes, rewriting paths to the root of the target service. The proxy listens on all network interfaces (0.0.0.0:6443) and uses an ad-hoc self-signed TLS certificate for HTTPS.

## Features
- **Proxy Routing**: Maps URL prefixes (e.g., /minikube, /api) to backend services with optional Bearer token authentication.
- **CORS Support**: Allows cross-origin requests, restricted to a single origin (https://portal.mechcloud.io by default).
- **TLS Enabled**: Runs with an ad-hoc self-signed certificate for HTTPS.
- **Flexible Path Handling**: Rewrites URLs to the root of the target service.
- **All IPs**: Listens on all network interfaces.

## Prerequisites
uv: A fast Python package and project manager (installation instructions below).

## Setup Instructions
Install uv using instructions from official docs - https://docs.astral.sh/uv/getting-started/installation

## Running proxy
### Clone repository
```
git clone git@github.com:mechcloud/mechcloud-flask-proxy.git
```

### Install dependencies and run the proxy
```
cd mechcloud-flask-proxy

uv venv
source .venv/bin/activate (non windows)
.venv\Scripts\activate (windows)
uv sync

uv run app.py
```

## Access the proxy
You can now access the proxy at `https://localhost:6443` url.

## Defining a route to a proxied api (make sure to restart after applying changes)
### Unsecured API
You can use following configuration to route requests to a (local) unsecured API -
```yaml
/minikube/:
  url: http://127.0.0.1:8001/
```

### Proteced API
You can use following configuration to route requests to a protected API secured using a bearer token -
```yaml
/k8s-1/:
  url: https://api.kubernetes-1.lab/
  token: <Bearer token>
```

