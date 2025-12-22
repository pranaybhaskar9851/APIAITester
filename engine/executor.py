
import requests, os, json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

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

    request_data = {
        "method": test["method"],
        "url": url,
        "headers": headers
    }

    try:
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
        
        # Print progress
        status_emoji = "✅" if result["passed"] else "❌"
        print(f"{status_emoji} {test['test_name']}: {r.status_code}")
        
        return result

    except Exception as e:
        result = {
            "id": test["id"],
            "name": test["test_name"],
            "passed": False,
            "error": str(e),
            "url": url
        }
        print(f"❌ {test['test_name']}: ERROR - {str(e)}")
        return result


def execute_tests(tests, api_key, base_url, run_id, max_workers=10):
    """Execute tests in parallel using ThreadPoolExecutor"""
    base_url = base_url.rstrip("/")
    run_dir = os.path.join("artifacts", run_id)
    os.makedirs(run_dir, exist_ok=True)

    results = []
    
    # Use the provided API key
    if not api_key or api_key.strip() == "":
        print("WARNING: No API key provided. Some endpoints may require authentication.")
        api_key = ""
    else:
        print(f"Using API key: {api_key[:10] if len(api_key) > 10 else api_key}...")

    # Execute all test cases in parallel
    print(f"\n🚀 Executing {len(tests)} test cases in parallel (max {max_workers} concurrent)...\n")
    
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
            except Exception as e:
                test = future_to_test[future]
                print(f"❌ {test['test_name']}: EXCEPTION - {str(e)}")
                results.append({
                    "id": test["id"],
                    "name": test["test_name"],
                    "passed": False,
                    "error": str(e),
                    "url": base_url + test["endpoint"]
                })
    
    elapsed_time = time.time() - start_time
    passed_count = sum(1 for r in results if r.get("passed"))
    failed_count = len(results) - passed_count
    
    print(f"\n{'='*60}")
    print(f"✨ Execution completed in {elapsed_time:.2f} seconds")
    print(f"📊 Results: {passed_count} passed, {failed_count} failed out of {len(results)} tests")
    print(f"{'='*60}\n")

    return results
