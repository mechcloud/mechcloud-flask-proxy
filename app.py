from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import logging
from urllib.parse import urljoin
import yaml
import os

app = Flask(__name__)
# Enable CORS for a single host
CORS(
   app, 
   origins=['https://portal.mechcloud.io'],
   supports_credentials=True
)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load proxy mappings from YAML file
def load_proxy_mappings():
    try:
        yaml_file_path = os.path.join(os.path.dirname(__file__), 'proxy.yaml')
        with open(yaml_file_path, 'r') as file:
            mappings = yaml.safe_load(file)
            # Ensure mappings is a dictionary
            if not isinstance(mappings, dict):
                logger.error("Invalid proxy.yaml format: root must be a mapping")
                return {}
            return mappings
    except FileNotFoundError:
        logger.error("proxy.yaml file not found")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing proxy.yaml: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading proxy.yaml: {str(e)}")
        return {}

# Load mappings at startup
PROXY_MAPPINGS = load_proxy_mappings()

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Flask API!'})

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    # Determine the proxy configuration based on the requested path
    for uri, config in PROXY_MAPPINGS.items():
        if path.startswith(uri.lstrip('/')):  # Match after removing leading slash from URI
            # Normalize the URI for stripping (remove leading/trailing slashes for matching)
            uri_stripped = uri.strip('/')
            # Compute rewritten path by removing the URI prefix
            rewritten_path = path[len(uri_stripped):].lstrip('/') if path[len(uri_stripped):] else ''
            
            # Construct target URL using urljoin
            base_url = config['url'].rstrip('/')  # Normalize base URL
            target_url = urljoin(base_url + '/', rewritten_path) if rewritten_path else base_url + '/'
            
            # Prepare headers, including Bearer token if present
            headers = {key: value for key, value in request.headers if key != 'Host'}
            if 'token' in config and config['token']:
                headers['Authorization'] = f"Bearer {config['token']}"
            
            # Log the proxied request
            logger.debug(f"Proxying {request.method} to {target_url} with headers: {headers}")
            
            # Forward the request to the proxy
            try:
                # Buffer the response fully, no streaming
                response = requests.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    data=request.get_data(),
                    cookies=request.cookies,
                    allow_redirects=False
                )
                
                # Log the backend response
                logger.debug(f"Backend response: status={response.status_code}, headers={response.headers}")
                
                # Get the response body
                content = response.content
                
                # Prepare headers: only include Content-Type if present
                response_headers = []
                if 'Content-Type' in response.headers:
                    response_headers.append(('Content-Type', response.headers['Content-Type']))
                
                # Create Flask response with status, Content-Type, and body
                flask_response = app.response_class(
                    response=content,
                    status=response.status_code,
                    headers=response_headers
                )
                
                return flask_response
            except requests.RequestException as e:
                logger.error(f"Proxy request failed: {str(e)}")
                return jsonify({'error': f'Proxy request failed: {str(e)}'}), 502
    
    return jsonify({'error': 'No matching proxy route found'}), 404

if __name__ == '__main__':
    # Listen on all IPs (0.0.0.0) and enable TLS with ad-hoc self-signed certificate
    app.run(host='0.0.0.0', port=6443, debug=True, ssl_context='adhoc')

