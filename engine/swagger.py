
import requests

def load_swagger(swagger_input: str) -> dict:
    resp = requests.get(swagger_input, timeout=20)
    resp.raise_for_status()
    return resp.json()

def resolve_ref(swagger: dict, ref_path: str):
    """
    Resolve a $ref path like '#/components/schemas/Pet' to the actual schema object.
    """
    if not ref_path or not ref_path.startswith('#/'):
        return None
    
    parts = ref_path[2:].split('/')  # Remove '#/' and split by '/'
    current = swagger
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    
    return current

def generate_sample_data(swagger: dict, schema: dict, depth=0, max_depth=3):
    """
    Generate sample data based on a JSON schema.
    Handles types: object, array, string, integer, number, boolean
    Resolves $ref references.
    """
    # Prevent infinite recursion
    if depth > max_depth:
        return None
    
    # Handle $ref
    if '$ref' in schema:
        resolved_schema = resolve_ref(swagger, schema['$ref'])
        if resolved_schema:
            return generate_sample_data(swagger, resolved_schema, depth + 1, max_depth)
        return None
    
    schema_type = schema.get('type', 'object')
    
    # Handle different types
    if schema_type == 'object':
        obj = {}
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])
        
        for prop_name, prop_schema in properties.items():
            # Only include required fields or first few properties
            if prop_name in required_fields or len(obj) < 5:
                value = generate_sample_data(swagger, prop_schema, depth + 1, max_depth)
                if value is not None:
                    obj[prop_name] = value
        
        return obj if obj else {}
    
    elif schema_type == 'array':
        items_schema = schema.get('items', {})
        # Generate one sample item
        sample_item = generate_sample_data(swagger, items_schema, depth + 1, max_depth)
        return [sample_item] if sample_item is not None else []
    
    elif schema_type == 'string':
        # Use example, default, or enum values if available
        if 'example' in schema:
            return schema['example']
        elif 'default' in schema:
            return schema['default']
        elif 'enum' in schema and schema['enum']:
            return schema['enum'][0]
        else:
            return "string"
    
    elif schema_type == 'integer':
        if 'example' in schema:
            return schema['example']
        elif 'default' in schema:
            return schema['default']
        else:
            return 0
    
    elif schema_type == 'number':
        if 'example' in schema:
            return schema['example']
        elif 'default' in schema:
            return schema['default']
        else:
            return 0.0
    
    elif schema_type == 'boolean':
        if 'default' in schema:
            return schema['default']
        else:
            return False
    
    return None

def get_request_body_schema(swagger: dict, path: str, method: str):
    """
    Extract the request body schema for a given path and method.
    Returns the schema object or None if no request body.
    """
    try:
        paths = swagger.get('paths', {})
        if path not in paths:
            return None
        
        method_spec = paths[path].get(method.lower(), {})
        request_body = method_spec.get('requestBody', {})
        
        if not request_body:
            return None
        
        # Get the schema from content type (prefer application/json)
        content = request_body.get('content', {})
        
        if 'application/json' in content:
            return content['application/json'].get('schema', {})
        elif 'application/xml' in content:
            return content['application/xml'].get('schema', {})
        elif content:
            # Get first available content type
            first_content = next(iter(content.values()))
            return first_content.get('schema', {})
        
        return None
    except (KeyError, AttributeError):
        return None
