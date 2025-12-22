
import requests

def load_swagger(swagger_input: str) -> dict:
    resp = requests.get(swagger_input, timeout=20)
    resp.raise_for_status()
    return resp.json()
