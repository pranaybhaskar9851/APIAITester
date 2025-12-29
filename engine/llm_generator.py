
import json
import ollama

def generate_tests_with_llm(swagger: dict, login_endpoint=None, model="llama3.2"):
    """
    Generate API test cases using a local Ollama LLM model.
    The LLM analyzes the Swagger spec and creates intelligent test scenarios.
    """
    
    # Get all paths from Swagger
    paths = swagger.get("paths", {})
    test_counter = 1
    
    # Normalize login_endpoint for exclusion
    login_path = login_endpoint.strip() if login_endpoint else None
    
    # Calculate expected test count (2 tests per endpoint per method)
    expected_test_count = 0
    for path, methods in paths.items():
        for method in methods:
            if method.lower() in ["get", "post", "put", "delete", "patch"]:
                expected_test_count += 2  # positive + unauthorized
    
    print(f"\n[LLM] Using {model} to generate tests for {len(paths)} endpoints...")
    print(f"Expected ~{expected_test_count} test cases")
    print("Processing all endpoints in a single batch for faster execution\n")
    
    # Process all endpoints at once for faster execution
    all_tests, test_counter = generate_batch_with_llm(paths, swagger.get("info", {}), login_path, model, 1, 1, test_counter)
    
    # Check if LLM generated significantly fewer tests than expected
    if all_tests and len(all_tests) < expected_test_count * 0.8:  # Less than 80% of expected
        print(f"\nWARNING: LLM generated only {len(all_tests)}/{expected_test_count} expected tests")
        print("Falling back to rule-based generation to ensure complete coverage\n")
        return generate_basic_tests_fallback(swagger, login_endpoint)
    
    # If LLM completely failed, fall back to basic generation
    if not all_tests:
        print("WARNING: LLM generation produced no valid tests. Using fallback generation...")
        return generate_basic_tests_fallback(swagger, login_endpoint)
    
    print(f"SUCCESS: LLM generated {len(all_tests)} test cases successfully")
    return all_tests


def generate_batch_with_llm(paths_batch: dict, api_info: dict, login_endpoint: str, model: str, batch_num: int, total_batches: int, test_counter: int):
    """
    Generate test cases for a batch of endpoints using LLM.
    """
    
    # Create simplified spec for this batch
    batch_spec = {
        "paths": paths_batch
    }
    swagger_str = json.dumps(batch_spec, indent=2)
    
    # Create the prompt for the LLM - simplified for faster processing
    prompt = f"""Generate API test cases. For EACH endpoint and method below, create EXACTLY 2 tests: one with valid auth (expect 200), one with invalid auth (expect 401).

{swagger_str}

Rules:
- Replace path params like {{id}} with "1"
- Skip query params unless required
- Return ONLY a JSON array, nothing else

[{{"id":"test001","test_name":"GET /path - Positive Test","method":"GET","endpoint":"/path","expected_status":200,"auth":"valid","headers":{{"accept":"application/json"}}}},{{"id":"test002","test_name":"GET /path - Unauthorized Test","method":"GET","endpoint":"/path","expected_status":401,"auth":"invalid","headers":{{"accept":"application/json"}}}}]

Your JSON array:"""

    try:
        print(f"  Processing {len(paths_batch)} endpoints (batch {batch_num}/{total_batches})...")
        
        # Call Ollama API with optimized parameters
        response = ollama.chat(
            model=model,
            messages=[{
                'role': 'user',
                'content': prompt
            }],
            options={
                'temperature': 0,  # Faster and more deterministic
                'num_predict': 16384,  # Increased for all endpoints at once
                'num_ctx': 8192  # Increased context window
            }
        )
        
        # Extract the response content
        llm_output = response['message']['content']
        
        # Try to parse the JSON response
        # Sometimes LLMs wrap JSON in markdown code blocks
        if '```json' in llm_output:
            llm_output = llm_output.split('```json')[1].split('```')[0].strip()
        elif '```' in llm_output:
            llm_output = llm_output.split('```')[1].split('```')[0].strip()
        
        # Clean up common issues
        llm_output = llm_output.strip()
        if not llm_output.startswith('['):
            # Try to find the JSON array start
            start_idx = llm_output.find('[')
            if start_idx != -1:
                llm_output = llm_output[start_idx:]
        
        tests = json.loads(llm_output)
        
        # Validate and ensure all tests have required fields
        validated_tests = []
        for test in tests:
            if all(k in test for k in ['method', 'endpoint', 'expected_status']):
                # Ensure test has all required fields with defaults
                validated_test = {
                    "id": f"test{test_counter:03d}",
                    "test_name": test.get("test_name", f"{test['method']} {test['endpoint']}"),
                    "method": test["method"],
                    "endpoint": test["endpoint"],
                    "expected_status": test["expected_status"],
                    "auth": test.get("auth", "valid"),
                    "headers": test.get("headers", {
                        "accept": "application/json",
                        "Content-Type": "application/json",
                        "Locale": "en_US"
                    })
                }
                validated_tests.append(validated_test)
                test_counter += 1
            else:
                print(f"    WARNING: Skipping invalid test: missing required fields {[k for k in ['method', 'endpoint', 'expected_status'] if k not in test]}")
        
        if validated_tests:
            print(f"  SUCCESS: Batch {batch_num} generated {len(validated_tests)} test cases")
        else:
            print(f"  WARNING: Batch {batch_num} generated 0 valid test cases")
        
        return validated_tests, test_counter
        
    except json.JSONDecodeError as e:
        print(f"  ERROR: Batch {batch_num} JSON parse error: {e}")
        print(f"  LLM Output preview: {llm_output[:500] if 'llm_output' in locals() else 'N/A'}...")
        print(f"  TIP: The LLM might be generating invalid JSON. Consider using rule-based generation instead.")
        return [], test_counter
        
    except Exception as e:
        print(f"  ERROR: Batch {batch_num} error: {type(e).__name__}: {e}")
        print(f"  TIP: Check if Ollama is running and the model '{model}' is available")
        return [], test_counter


def generate_basic_tests_fallback(swagger: dict, login_endpoint=None):
    """
    Fallback method if LLM fails - generates basic test cases from Swagger
    """
    from engine.generator import generate_tests
    return generate_tests(swagger, login_endpoint)
