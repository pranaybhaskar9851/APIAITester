
import requests, os, json
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Configure stdout to handle encoding errors gracefully on Windows
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

# Thread-safe lock for file writing
file_lock = Lock()

def execute_single_test(test, api_key, base_url, run_dir):
    """Execute a single test case"""
    headers = dict(test.get("headers", {}))
    # Ensure required headers are present
    if "accept" not in headers:
        headers["accept"] = "application/json"
    
    # Add API key if provided and if test requires authentication
    if test["auth"] == "valid" and api_key:
        headers["api_key"] = api_key
    elif test["auth"] != "valid":
        # For invalid auth tests, use invalid API key
        headers["api_key"] = "invalid"

    url = base_url + test["endpoint"]

    # Prepare request data
    request_data = {
        "method": test["method"],
        "url": url,
        "headers": headers
    }
    
    # Add body if present
    body_json = None
    if "body" in test:
        body_json = test["body"]
        request_data["body"] = body_json

    try:
        # Make request with or without body
        if body_json is not None:
            r = requests.request(
                test["method"],
                url,
                headers=headers,
                json=body_json,
                timeout=30
            )
        else:
            r = requests.request(
                test["method"],
                url,
                headers=headers,
                timeout=30
            )

        response_data = {
            "status_code": r.status_code,
            "headers": dict(r.headers),
            "body": r.text
        }

        # Thread-safe file writing
        with file_lock:
            with open(os.path.join(run_dir, f"{test['id']}_request.json"), "w") as f:
                json.dump(request_data, f, indent=2)

            with open(os.path.join(run_dir, f"{test['id']}_response.json"), "w") as f:
                json.dump(response_data, f, indent=2)

        result = {
            "id": test["id"],
            "name": test["test_name"],
            "expected": test["expected_status"],
            "actual": r.status_code,
            "passed": r.status_code == test["expected_status"],
            "url": url
        }
        
        # Print progress with safe encoding
        status = "PASS" if result["passed"] else "FAIL"
        try:
            print(f"[{status}] {test['test_name']}: {r.status_code}", flush=True)
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Fallback for Windows console encoding issues
            safe_name = test['test_name'].encode('ascii', errors='replace').decode('ascii')
            print(f"[{status}] {safe_name}: {r.status_code}", flush=True)
        
        return result

    except Exception as e:
        result = {
            "id": test["id"],
            "name": test["test_name"],
            "passed": False,
            "error": str(e),
            "url": url
        }
        # Print error with safe encoding
        try:
            print(f"[FAIL] {test['test_name']}: ERROR - {str(e)}", flush=True)
        except (UnicodeEncodeError, UnicodeDecodeError):
            safe_name = test['test_name'].encode('ascii', errors='replace').decode('ascii')
            safe_error = str(e).encode('ascii', errors='replace').decode('ascii')
            print(f"[FAIL] {safe_name}: ERROR - {safe_error}", flush=True)
        return result


def execute_tests(tests, api_key, base_url, run_id, max_workers=10):
    """Execute tests in parallel using ThreadPoolExecutor"""
    base_url = base_url.rstrip("/")
    run_dir = os.path.join("artifacts", run_id)
    os.makedirs(run_dir, exist_ok=True)

    results = []
    completed_count = 0
    passed_count = 0
    failed_count = 0
    
    # Use the provided API key
    if not api_key or api_key.strip() == "":
        print("WARNING: No API key provided. Some endpoints may require authentication.", flush=True)
        api_key = ""
    else:
        print(f"Using API key: {api_key[:10] if len(api_key) > 10 else api_key}...", flush=True)

    # Execute all test cases in parallel
    print(f"\n{'='*70}", flush=True)
    print(f"STARTING TEST EXECUTION", flush=True)
    print(f"{'='*70}", flush=True)
    print(f"Total Tests: {len(tests)}", flush=True)
    print(f"Parallel Workers: {max_workers}", flush=True)
    print(f"Base URL: {base_url}", flush=True)
    print(f"Artifacts: {run_dir}", flush=True)
    print(f"{'='*70}\n", flush=True)
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tests
        future_to_test = {
            executor.submit(execute_single_test, test, api_key, base_url, run_dir): test 
            for test in tests
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_test):
            try:
                result = future.result()
                results.append(result)
                completed_count += 1
                
                if result.get("passed"):
                    passed_count += 1
                else:
                    failed_count += 1
                
                # Print progress update
                progress_pct = (completed_count / len(tests)) * 100
                print(f"[{completed_count}/{len(tests)}] ({progress_pct:.1f}%) - Pass: {passed_count}, Fail: {failed_count}", flush=True)
                
            except Exception as e:
                test = future_to_test[future]
                completed_count += 1
                failed_count += 1
                print(f"[{completed_count}/{len(tests)}] ERROR: {test['test_name']}: EXCEPTION - {str(e)}", flush=True)
                results.append({
                    "id": test["id"],
                    "name": test["test_name"],
                    "passed": False,
                    "error": str(e),
                    "url": base_url + test["endpoint"]
                })
    
    elapsed_time = time.time() - start_time
    
    print(f"\n{'='*70}", flush=True)
    print(f"TEST EXECUTION COMPLETED", flush=True)
    print(f"{'='*70}", flush=True)
    print(f"Total Time: {elapsed_time:.2f} seconds", flush=True)
    print(f"Avg Time per Test: {elapsed_time/len(results):.2f} seconds", flush=True)
    print(f"", flush=True)
    print(f"Results Summary:", flush=True)
    print(f"  ✓ Passed: {passed_count}/{len(results)} ({passed_count/len(results)*100:.1f}%)", flush=True)
    print(f"  ✗ Failed: {failed_count}/{len(results)} ({failed_count/len(results)*100:.1f}%)", flush=True)
    print(f"{'='*70}\n", flush=True)

    return results
