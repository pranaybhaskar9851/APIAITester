from engine.swagger import get_request_body_schema, generate_sample_data

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

            # Generate request body for POST/PUT/PATCH methods
            request_body = None
            if method.lower() in ['post', 'put', 'patch']:
                schema = get_request_body_schema(swagger, path, method)
                if schema:
                    request_body = generate_sample_data(swagger, schema)

            # Create positive test
            expected_status = 201 if method.lower() == 'post' else 200
            test_case = {
                "id": f"test{test_counter:03d}",
                "test_name": f"{method.upper()} {path} - Valid Request",
                "method": method.upper(),
                "endpoint": endpoint,
                "expected_status": expected_status,
                "auth": "valid",
                "headers": {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                    "Locale": "en_US"
                }
            }
            if request_body:
                test_case["body"] = request_body
            
            tests.append(test_case)
            test_counter += 1

            # Create negative test based on method type
            if method.lower() == 'get':
                # For GET: test unauthorized access
                negative_test = {
                    "id": f"test{test_counter:03d}",
                    "test_name": f"{method.upper()} {path} - Unauthorized",
                    "method": method.upper(),
                    "endpoint": endpoint,
                    "expected_status": 401,
                    "auth": "invalid",
                    "headers": {
                        "accept": "application/json",
                        "Content-Type": "application/json",
                        "Locale": "en_US"
                    }
                }
            else:
                # For POST/PUT/DELETE/PATCH: test with invalid/non-existent resource
                invalid_endpoint = endpoint
                # Replace path parameters with non-existent IDs
                if "{" in path:
                    # Use 999999 for non-existent resource
                    invalid_endpoint = endpoint.replace("/1", "/999999")
                else:
                    # For endpoints without params, use invalid data in body
                    invalid_endpoint = endpoint
                
                negative_test = {
                    "id": f"test{test_counter:03d}",
                    "test_name": f"{method.upper()} {path} - Invalid Input",
                    "method": method.upper(),
                    "endpoint": invalid_endpoint,
                    "expected_status": 404 if method.lower() in ['put', 'delete'] else 400,
                    "auth": "valid",
                    "headers": {
                        "accept": "application/json",
                        "Content-Type": "application/json",
                        "Locale": "en_US"
                    }
                }
                
                # Add invalid body for POST/PUT/PATCH
                if request_body and method.lower() in ['post', 'put', 'patch']:
                    import random
                    invalid_body = request_body.copy() if isinstance(request_body, dict) else request_body
                    # Make the body invalid by setting required fields to invalid values
                    if isinstance(invalid_body, dict):
                        if 'id' in invalid_body:
                            invalid_body['id'] = random.randint(100000, 9999999)  # Random non-existent ID
                        if 'name' in invalid_body:
                            invalid_body['name'] = ""  # Empty name (often invalid)
                    negative_test["body"] = invalid_body
            
            tests.append(negative_test)
            test_counter += 1

    return tests
