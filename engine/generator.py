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
            
            # Keep all methods now that we have smart ID discovery and reuse
            # GET tests will run first to discover IDs, then POST/PUT/DELETE will use them

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
                            # Add value for string params (both required and optional)
                            if "enum" in param_schema and param_schema["enum"]:
                                param_value = param_schema["enum"][0]
                            else:
                                param_value = "available"  # Default string value
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

            # For POST and PUT, create 2 positive test scenarios
            # For other methods, create 1 positive test
            num_positive_tests = 2 if method.lower() in ['post', 'put'] else 1
            
            for i in range(num_positive_tests):
                expected_status = 201 if method.lower() == 'post' else 200
                test_name_suffix = f"Valid Request {i+1}" if num_positive_tests > 1 else "Valid Request"
                
                test_case = {
                    "id": f"test{test_counter:03d}",
                    "test_name": f"{method.upper()} {path} - {test_name_suffix}",
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
                # Many public APIs don't enforce auth, so we expect 200
                negative_test = {
                    "id": f"test{test_counter:03d}",
                    "test_name": f"{method.upper()} {path} - Unauthorized",
                    "method": method.upper(),
                    "endpoint": endpoint,
                    "expected_status": 200,  # Public API - expect 200 since no auth enforcement
                    "auth": "invalid",
                    "headers": {
                        "accept": "application/json",
                        "Content-Type": "application/json",
                        "Locale": "en_US"
                    }
                }
                tests.append(negative_test)
                test_counter += 1
                
            elif method.lower() == 'post':
                # For POST: test with invalid/missing required fields
                negative_endpoint = endpoint
                negative_test = {
                    "id": f"test{test_counter:03d}",
                    "test_name": f"{method.upper()} {path} - Invalid Body",
                    "method": method.upper(),
                    "endpoint": negative_endpoint,
                    "expected_status": 400,  # Bad request
                    "auth": "valid",
                    "headers": {
                        "accept": "application/json",
                        "Content-Type": "application/json",
                        "Locale": "en_US"
                    },
                    "body": {}  # Empty body to trigger validation error
                }
                tests.append(negative_test)
                test_counter += 1
                
            elif method.lower() in ['put', 'patch']:
                # For PUT/PATCH: test with non-existent ID
                negative_endpoint = endpoint.replace("/1", "/999999")
                if "{" not in path:  # Only if path doesn't have parameters
                    negative_endpoint = endpoint.replace("/1", "/999999")
                else:
                    # Replace the ID in original path
                    negative_endpoint = path
                    while "{" in negative_endpoint:
                        start = negative_endpoint.index("{")
                        end = negative_endpoint.index("}")
                        negative_endpoint = negative_endpoint[:start] + "999999" + negative_endpoint[end+1:]
                    # Add query params if original had them
                    if "?" in endpoint:
                        negative_endpoint += "?" + endpoint.split("?")[1]
                
                negative_test = {
                    "id": f"test{test_counter:03d}",
                    "test_name": f"{method.upper()} {path} - Invalid ID",
                    "method": method.upper(),
                    "endpoint": negative_endpoint,
                    "expected_status": 404,  # Not found
                    "auth": "valid",
                    "headers": {
                        "accept": "application/json",
                        "Content-Type": "application/json",
                        "Locale": "en_US"
                    }
                }
                if request_body:
                    negative_test["body"] = request_body
                tests.append(negative_test)
                test_counter += 1
                
            elif method.lower() == 'delete':
                # For DELETE: test with non-existent ID
                negative_endpoint = endpoint.replace("/1", "/999999")
                if "{" not in path:  # Only if path doesn't have parameters
                    negative_endpoint = endpoint.replace("/1", "/999999")
                else:
                    # Replace the ID in original path
                    negative_endpoint = path
                    while "{" in negative_endpoint:
                        start = negative_endpoint.index("{")
                        end = negative_endpoint.index("}")
                        negative_endpoint = negative_endpoint[:start] + "999999" + negative_endpoint[end+1:]
                    # Add query params if original had them
                    if "?" in endpoint:
                        negative_endpoint += "?" + endpoint.split("?")[1]
                
                negative_test = {
                    "id": f"test{test_counter:03d}",
                    "test_name": f"{method.upper()} {path} - Invalid ID",
                    "method": method.upper(),
                    "endpoint": negative_endpoint,
                    "expected_status": 404,  # Not found
                    "auth": "valid",
                    "headers": {
                        "accept": "application/json",
                        "Content-Type": "application/json",
                        "Locale": "en_US"
                    }
                }
                tests.append(negative_test)
                test_counter += 1

    return tests
