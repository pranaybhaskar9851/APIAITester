
def generate_tests(swagger: dict, login_endpoint=None):
    tests = []
    test_counter = 1
    paths = swagger.get("paths", {})
    
    # Normalize login_endpoint for comparison
    login_path = None
    if login_endpoint:
        # Remove leading slash if present for consistent comparison
        login_path = login_endpoint if not login_endpoint.startswith('/') else login_endpoint[1:]

    for path, methods in paths.items():
        # Skip the login endpoint from test generation
        path_normalized = path if not path.startswith('/') else path[1:]
        if login_path and path_normalized == login_path:
            print(f"Skipping login endpoint from tests: {path}")
            continue
            
        for method in methods:
            if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                continue

            endpoint = path
            while "{" in endpoint:
                start = endpoint.index("{")
                end = endpoint.index("}")
                endpoint = endpoint[:start] + "1" + endpoint[end+1:]
            
            # Extract query parameters from Swagger spec
            method_spec = methods[method]
            query_params = []
            if "parameters" in method_spec:
                for param in method_spec["parameters"]:
                    if param.get("in") == "query":
                        # Use default value or a reasonable value based on type
                        param_name = param.get("name")
                        param_schema = param.get("schema", {})
                        
                        # Check if parameter is required
                        is_required = param.get("required", False)
                        
                        # Get default value or generate appropriate value
                        if "default" in param_schema:
                            param_value = str(param_schema["default"]).lower() if isinstance(param_schema["default"], bool) else param_schema["default"]
                        elif param_schema.get("type") == "boolean":
                            param_value = "false"
                        elif param_schema.get("type") == "integer":
                            param_value = "10"
                        elif param_schema.get("type") == "number":
                            param_value = "10"
                        elif param_schema.get("type") == "string":
                            # Only add string params if they're required
                            if is_required:
                                param_value = ""
                            else:
                                continue  # Skip optional string params
                        else:
                            continue  # Skip unknown types
                        
                        query_params.append(f"{param_name}={param_value}")
            
            # Add query parameters to endpoint if any
            if query_params:
                endpoint += "?" + "&".join(query_params)

            tests.append({
                "id": f"test{test_counter:03d}",
                "test_name": f"{method.upper()} {path} - Positive Test",
                "method": method.upper(),
                "endpoint": endpoint,
                "expected_status": 200,
                "auth": "valid",
                "headers": {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                    "Locale": "en_US"
                }
            })
            test_counter += 1

            tests.append({
                "id": f"test{test_counter:03d}",
                "test_name": f"{method.upper()} {path} - Unauthorized Test",
                "method": method.upper(),
                "endpoint": endpoint,
                "expected_status": 401,
                "auth": "invalid",
                "headers": {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                    "Locale": "en_US"
                }
            })
            test_counter += 1

    return tests
