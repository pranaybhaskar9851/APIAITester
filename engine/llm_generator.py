
import json
import sys
import ollama
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from engine.swagger import get_request_body_schema, generate_sample_data

# Configure stdout to handle encoding errors gracefully on Windows
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

def fix_json_format(json_str):
    """
    Fix common JSON formatting issues from LLM output.
    Converts JavaScript-style syntax to valid JSON.
    """
    # Remove template literals and replace with empty strings or actual values
    json_str = re.sub(r'`([^`]*)`', r'"\1"', json_str)  # Replace backticks with double quotes
    
    # Fix template variable references like ${endpoint}
    json_str = re.sub(r'\$\{[^}]+\}', '""', json_str)
    
    # Fix unquoted property names (JavaScript style) - must come before value fixes
    # Match word characters followed by colon (not already quoted)
    json_str = re.sub(r'([,{]\s*)(\w+)(\s*:)', r'\1"\2"\3', json_str)
    
    # Fix unquoted single word values - more aggressive matching
    # Match standalone words on their own line or after colon
    json_str = re.sub(r':\s+(\w+)\s*,', r': "\1",', json_str)  # : word,
    json_str = re.sub(r':\s+(\w+)\s*\n', r': "\1"\n', json_str)  # : word\n
    json_str = re.sub(r':\s*(\w+)\s*([,}])', r': "\1"\2', json_str)  # Catch remaining
    
    # Fix boolean and null values that were incorrectly quoted
    json_str = json_str.replace('"true"', 'true')
    json_str = json_str.replace('"false"', 'false')
    json_str = json_str.replace('"null"', 'null')
    
    # Fix numbers that were incorrectly quoted (but keep string numbers)
    json_str = re.sub(r': "(\d+)"([,}\]])', r': \1\2', json_str)
    
    # Replace single quotes with double quotes
    json_str = json_str.replace("'", '"')
    
    # Remove trailing commas before closing brackets/braces
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    
    return json_str

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
    
    print(f"\n[LLM] Using {model} to generate tests for {len(paths)} endpoints...", flush=True)
    print(f"Expected ~{expected_test_count} test cases", flush=True)
    
    # Start timing
    start_time = time.time()
    
    # Process endpoints one at a time for maximum reliability
    batch_size = 1  # 1 endpoint at a time = guaranteed completion
    all_tests = []
    path_items = list(paths.items())
    total_batches = (len(path_items) + batch_size - 1) // batch_size
    
    print(f"Processing {len(paths)} endpoints in {total_batches} batches of up to {batch_size} endpoints each\n", flush=True)
    print(f"Running 2 batches in parallel for faster processing...\n", flush=True)
    
    # Process with 2 parallel batches at a time
    lock = Lock()
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        
        for i in range(0, len(path_items), batch_size):
            batch_paths = dict(path_items[i:i + batch_size])
            batch_num = (i // batch_size) + 1
            
            future = executor.submit(
                generate_batch_with_llm,
                batch_paths,
                swagger,
                login_path,
                model,
                batch_num,
                total_batches,
                test_counter
            )
            futures.append((future, batch_num))
        
        # Collect results as they complete
        for future, batch_num in futures:
            try:
                batch_tests, test_counter = future.result(timeout=300)
                
                if batch_tests:
                    with lock:
                        all_tests.extend(batch_tests)
                    print(f"  ✓ Batch {batch_num}: Added {len(batch_tests)} tests (Total so far: {len(all_tests)})\n", flush=True)
                else:
                    print(f"  ✗ Batch {batch_num}: Generated 0 tests (skipping)\n", flush=True)
            except Exception as e:
                print(f"  ✗ Batch {batch_num}: ERROR - {e}\n", flush=True)
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    # Re-number test IDs sequentially to avoid gaps from parallel processing
    for idx, test in enumerate(all_tests, 1):
        test['id'] = f"test{idx:03d}"
    
    # Report results (no fallback - use LLM results only)
    if not all_tests:
        print(f"\nERROR: LLM generation failed to produce any valid tests (took {elapsed_time:.1f}s)", flush=True)
        print("TIP: Check if Ollama is running and the model is available", flush=True)
        return []
    
    if len(all_tests) < expected_test_count:
        print(f"\nWARNING: LLM generated {len(all_tests)}/{expected_test_count} expected tests (took {elapsed_time:.1f}s)", flush=True)
        print("TIP: Increase num_predict tokens or use a larger model for better coverage", flush=True)
    else:
        print(f"\nSUCCESS: LLM generated {len(all_tests)} test cases in {elapsed_time:.1f} seconds", flush=True)
    
    return all_tests


def generate_batch_with_llm(paths_batch: dict, swagger: dict, login_endpoint: str, model: str, batch_num: int, total_batches: int, test_counter: int):
    """
    Generate test cases for a batch of endpoints using LLM.
    """
    
    # Create simplified spec for this batch with schema information
    batch_spec = {
        "paths": paths_batch
    }
    
    # Count total methods (each path+method combination is an endpoint)
    method_count = 0
    endpoint_list = []
    expected_tests = 0
    for path, methods in paths_batch.items():
        for method in methods:
            if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                method_count += 1
                endpoint_list.append(f"{method.upper()} {path}")
                # Calculate expected tests based on method type (matching rule-based generator)
                if method.lower() == 'get':
                    expected_tests += 2  # 1 valid + 1 unauthorized
                elif method.lower() == 'post':
                    expected_tests += 3  # 2 valid + 1 invalid body
                elif method.lower() in ['put', 'patch']:
                    expected_tests += 3  # 2 valid + 1 invalid ID
                elif method.lower() == 'delete':
                    expected_tests += 2  # 1 valid + 1 invalid ID
    
    print(f"  DEBUG: Batch {batch_num} endpoints: {endpoint_list}", flush=True)
    print(f"  DEBUG: Expected tests: {expected_tests}", flush=True)
    
    # Add example request bodies for POST/PUT/PATCH endpoints
    request_body_examples = {}
    for path, methods in paths_batch.items():
        for method in methods:
            if method.lower() in ['post', 'put', 'patch']:
                schema = get_request_body_schema(swagger, path, method)
                if schema:
                    sample_data = generate_sample_data(swagger, schema)
                    if sample_data:
                        request_body_examples[f"{method.upper()} {path}"] = sample_data
    
    swagger_str = json.dumps(batch_spec, indent=2)
    
    # endpoint_count is for display, expected_tests is accurately calculated above
    endpoint_count = method_count  # Count methods, not paths
    
    examples_str = ""
    if request_body_examples:
        examples_str = "\n\nRequest Body Examples (use these for POST/PUT/PATCH):\n" + json.dumps(request_body_examples, indent=2)
    
    prompt = f"""Generate EXACTLY {expected_tests} test cases in valid JSON array format.

OPERATIONS ({endpoint_count} total):
{chr(10).join(f"{i+1}. {ep}" for i, ep in enumerate(endpoint_list))}

CRITICAL: Use the EXACT endpoint path as listed above for each test. For example:
- If the operation is "GET /products/{{{{id}}}}", the endpoint in your test MUST be "/products/{{{{id}}}}" (then replace {{{{id}}}} with 1 or 999999)
- If the operation is "POST /products", the endpoint MUST be "/products" (no ID)
- DO NOT add or remove path segments

TEST RULES PER METHOD:
• GET: 2 tests (Valid Request + Unauthorized)
• POST: 3 tests (Valid Request 1 + Valid Request 2 + Invalid Body)
• PUT: 3 tests (Valid Request 1 + Valid Request 2 + Invalid ID)
• DELETE: 2 tests (Valid Request + Invalid ID)
• PATCH: 3 tests (same as PUT)

DETAILED RULES:
GET Method:
  1. Valid: endpoint with {{{{id}}}}→1, status 200, auth="valid", NO body
  2. Unauthorized: same endpoint, status 200, auth="invalid", NO body

POST Method:
  1. Valid Request 1: status 201, auth="valid", FULL body from examples
  2. Valid Request 2: status 201, auth="valid", FULL body from examples
  3. Invalid Body: status 400, auth="valid", body={{}}

PUT/PATCH Method:
  1. Valid Request 1: {{{{id}}}}→1, status 200, auth="valid", FULL body from examples
  2. Valid Request 2: {{{{id}}}}→1, status 200, auth="valid", FULL body from examples
  3. Invalid ID: {{{{id}}}}→999999, status 404, auth="valid", FULL body from examples

DELETE Method:
  1. Valid Request: {{{{id}}}}→1, status 200, auth="valid", NO body
  2. Invalid ID: {{{{id}}}}→999999, status 404, auth="valid", NO body{examples_str}

JSON TEMPLATE:
{{"id":"test001","test_name":"<METHOD> <path> - <Type>","method":"<METHOD>","endpoint":"<path>","expected_status":<code>,"auth":"valid","headers":{{"accept":"application/json","Content-Type":"application/json","Locale":"en_US"}}}}

Output {expected_tests} tests as JSON array:"""

    try:
        batch_start = time.time()
        print(f"  Processing {len(paths_batch)} endpoints (batch {batch_num}/{total_batches})...", flush=True)
        
        # Call Ollama API with optimized parameters for SPEED
        response = ollama.chat(
            model=model,
            messages=[{
                'role': 'user',
                'content': prompt
            }],
            options={
                'temperature': 0.1,
                'num_predict': 32768,  # Maximum limit to ensure complete generation
                'num_ctx': 16384
            }
        )
        
        batch_time = time.time() - batch_start
        
        # Extract the response content
        llm_output = response['message']['content']
        print(f"  LLM response received ({len(llm_output)} chars, {batch_time:.1f}s)", flush=True)
        
        # Extract JSON array with improved logic
        original_output = llm_output
        
        # Remove markdown code blocks
        if '```json' in llm_output:
            llm_output = llm_output.split('```json')[1].split('```')[0].strip()
        elif '```' in llm_output:
            llm_output = llm_output.split('```')[1].split('```')[0].strip()
        
        # Find the JSON array boundaries
        llm_output = llm_output.strip()
        start_idx = llm_output.find('[')
        if start_idx == -1:
            raise ValueError("No JSON array found in LLM output")
        
        # Find the matching closing bracket
        llm_output = llm_output[start_idx:]
        bracket_count = 0
        end_idx = -1
        in_string = False
        escape_next = False
        
        for i, char in enumerate(llm_output):
            if escape_next:
                escape_next = False
                continue
            if char == '\\':
                escape_next = True
                continue
            if char == '"' and not escape_next:
                in_string = not in_string
            if not in_string:
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_idx = i + 1
                        break
        
        if end_idx > 0:
            llm_output = llm_output[:end_idx]
        
        # Try to fix common JSON errors before parsing
        llm_output = fix_json_format(llm_output)
        
        tests = json.loads(llm_output)
        
        print(f"  Raw LLM output: {len(tests)} test objects parsed", flush=True)
        
        # Validate against expected test count (NOT endpoint count!)
        if len(tests) > expected_tests:
            print(f"  WARNING: LLM generated {len(tests)} tests, limiting to {expected_tests}", flush=True)
            tests = tests[:expected_tests]
        elif len(tests) < expected_tests:
            print(f"  WARNING: LLM only generated {len(tests)}/{expected_tests} expected tests", flush=True)
        
        # Validate and ensure all tests have required fields
        validated_tests = []
        skipped_count = 0
        methods_generated = {}
        for idx, test in enumerate(tests, 1):
            if all(k in test for k in ['method', 'endpoint', 'expected_status']):
                endpoint = test['endpoint']
                method = test['method'].upper()
                
                # Track methods being generated
                methods_generated[method] = methods_generated.get(method, 0) + 1
                
                # Skip tests with empty or invalid endpoints
                if not endpoint or not isinstance(endpoint, str) or endpoint.strip() in ["", '""', "null"]:
                    print(f"    SKIPPED test {idx}: Empty endpoint", flush=True)
                    skipped_count += 1
                    continue
                
                # Ensure endpoint starts with /
                endpoint = endpoint.strip()
                if not endpoint.startswith('/'):
                    endpoint = '/' + endpoint
                
                # Replace path parameters if they still have {}
                import random
                endpoint = re.sub(r'\{[^}]+\}', lambda m: '1' if 'valid' in test.get('test_name', '').lower() else str(random.randint(100000, 999999)), endpoint)
                
                # Ensure test has all required fields with defaults
                validated_test = {
                    "id": f"test{test_counter:03d}",
                    "test_name": test.get("test_name", f"{test['method']} {endpoint}"),
                    "method": test["method"].upper(),
                    "endpoint": endpoint,
                    "expected_status": int(test["expected_status"]) if isinstance(test["expected_status"], str) else test["expected_status"],
                    "auth": test.get("auth", "valid"),
                    "headers": test.get("headers", {
                        "accept": "application/json",
                        "Content-Type": "application/json",
                        "Locale": "en_US"
                    })
                }
                # Add body if present and not empty
                if "body" in test and test["body"]:
                    validated_test["body"] = test["body"]
                
                validated_tests.append(validated_test)
                test_counter += 1
            else:
                missing = [k for k in ['method', 'endpoint', 'expected_status'] if k not in test]
                print(f"    SKIPPED test {idx}: Missing {missing}", flush=True)
                skipped_count += 1
        
        if skipped_count > 0:
            print(f"  Total skipped: {skipped_count}, Valid tests: {len(validated_tests)}", flush=True)
        
        print(f"  Methods generated: {methods_generated}", flush=True)
        
        if validated_tests:
            print(f"  SUCCESS: Batch {batch_num} generated {len(validated_tests)} test cases in {batch_time:.1f}s", flush=True)
        else:
            print(f"  WARNING: Batch {batch_num} generated 0 valid test cases (took {batch_time:.1f}s)", flush=True)
        
        return validated_tests, test_counter
        
    except json.JSONDecodeError as e:
        print(f"  ERROR: Batch {batch_num} JSON parse error: {e}", flush=True)
        if 'llm_output' in locals():
            print(f"  Extracted JSON length: {len(llm_output)} chars", flush=True)
            print(f"  JSON preview (first 300 chars): {llm_output[:300]}...", flush=True)
            print(f"  JSON preview (last 200 chars): ...{llm_output[-200:]}", flush=True)
        if 'original_output' in locals():
            print(f"  Original LLM output length: {len(original_output)} chars", flush=True)
            # Show what caused the error
            print(f"  ERROR at position {e.pos}: {original_output[max(0,e.pos-50):min(len(original_output),e.pos+50)]}", flush=True)
        print(f"  TIP: Model '{model}' may not be good at JSON. Try 'qwen2.5:0.5b' or 'llama3.2:1b'", flush=True)
        return [], test_counter
        
    except Exception as e:
        print(f"  ERROR: Batch {batch_num} error: {type(e).__name__}: {e}", flush=True)
        if 'llm_output' in locals():
            print(f"  LLM output preview: {llm_output[:200] if llm_output else 'None'}...", flush=True)
        print(f"  TIP: Check if Ollama is running and the model '{model}' is available", flush=True)
        return [], test_counter


def generate_basic_tests_fallback(swagger: dict, login_endpoint=None):
    """
    Fallback method if LLM fails - generates basic test cases from Swagger
    """
    from engine.generator import generate_tests
    return generate_tests(swagger, login_endpoint)
