
import json
import sys
import ollama
import time

# Configure stdout to handle encoding errors gracefully on Windows
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

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
    print("⚡ FASTEST (<90s): qwen2:0.5b, tinyllama:latest")
    print("✓ GOOD (90-180s): llama3.2:1b, gemma2:2b")
    print("✓ ACCEPTABLE (180-300s): llama3:8b, gemma3:1b")
    print("✗ AVOID (>300s): phi3\n")
    
    # Start timing
    start_time = time.time()
    
    # Process endpoints in small batches for faster response times
    batch_size = 2  # Small batches = faster per-batch execution
    all_tests = []
    path_items = list(paths.items())
    total_batches = (len(path_items) + batch_size - 1) // batch_size
    
    print(f"Processing {len(paths)} endpoints in {total_batches} batches of up to {batch_size} endpoints each\n")
    
    for i in range(0, len(path_items), batch_size):
        batch_paths = dict(path_items[i:i + batch_size])
        batch_num = (i // batch_size) + 1
        
        batch_tests, test_counter = generate_batch_with_llm(
            batch_paths, 
            swagger.get("info", {}), 
            login_path, 
            model, 
            batch_num, 
            total_batches, 
            test_counter
        )
        all_tests.extend(batch_tests)
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    # Report results (no fallback - use LLM results only)
    if not all_tests:
        print(f"\nERROR: LLM generation failed to produce any valid tests (took {elapsed_time:.1f}s)")
        print("TIP: Check if Ollama is running and the model is available")
        print("TIP: Try a different model like qwen2:0.5b or tinyllama")
        return []
    
    if len(all_tests) < expected_test_count:
        print(f"\nWARNING: LLM generated {len(all_tests)}/{expected_test_count} expected tests (took {elapsed_time:.1f}s)")
        print("TIP: Increase num_predict tokens or use a larger model for better coverage")
    else:
        print(f"\nSUCCESS: LLM generated {len(all_tests)} test cases in {elapsed_time:.1f} seconds")
    
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
    prompt = f"""Generate test cases for the API endpoints below. For EACH endpoint and method, create exactly 2 tests:
1. Positive test with valid auth (expect 200)
2. Negative test with invalid auth (expect 401)

Endpoints:
{swagger_str}

IMPORTANT:
- Replace path parameters like {{id}} or {{petId}} with "1"
- Use simple headers: {{"accept": "application/json"}}
- Return ONLY a valid JSON array, no explanation

Example format:
[
  {{"id":"test001","test_name":"GET /pet/1 - Valid Auth","method":"GET","endpoint":"/pet/1","expected_status":200,"auth":"valid","headers":{{"accept":"application/json"}}}},
  {{"id":"test002","test_name":"GET /pet/1 - Invalid Auth","method":"GET","endpoint":"/pet/1","expected_status":401,"auth":"invalid","headers":{{"accept":"application/json"}}}}
]

Generate the JSON array now:"""

    try:
        batch_start = time.time()
        print(f"  Processing {len(paths_batch)} endpoints (batch {batch_num}/{total_batches})...")
        
        # Call Ollama API with optimized parameters for SPEED
        response = ollama.chat(
            model=model,
            messages=[{
                'role': 'user',
                'content': prompt
            }],
            options={
                'temperature': 0.1,
                'num_predict': 16384,  # Increased for all endpoints at once
                'num_ctx': 8192 # Increased context window
            }
        )
        
        batch_time = time.time() - batch_start
        
        # Extract the response content
        llm_output = response['message']['content']
        print(f"  LLM response received ({len(llm_output)} chars, {batch_time:.1f}s)")
        
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
            print(f"  SUCCESS: Batch {batch_num} generated {len(validated_tests)} test cases in {batch_time:.1f}s")
        else:
            print(f"  WARNING: Batch {batch_num} generated 0 valid test cases (took {batch_time:.1f}s)")
        
        return validated_tests, test_counter
        
    except json.JSONDecodeError as e:
        print(f"  ERROR: Batch {batch_num} JSON parse error: {e}")
        if 'llm_output' in locals():
            print(f"  Extracted JSON length: {len(llm_output)} chars")
            print(f"  JSON preview (first 300 chars): {llm_output[:300]}...")
            print(f"  JSON preview (last 200 chars): ...{llm_output[-200:]}")
        if 'original_output' in locals():
            print(f"  Original LLM output length: {len(original_output)} chars")
        print(f"  TIP: Try using 'llama3.2:1b' or 'qwen2.5:0.5b' for better JSON compliance")
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
