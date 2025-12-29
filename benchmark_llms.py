"""
Benchmark script to test all LLM models and measure their performance
"""
import requests
import time
import json
from datetime import datetime

# Configuration
BASE_API_URL = "http://127.0.0.1:8000"
SWAGGER_URL = "https://petstore3.swagger.io/api/v3/openapi.json"
BASE_URL = "https://petstore3.swagger.io/api/v3"
API_KEY = "test-api-key"

# Models to test
MODELS = [
    "qwen2.5:0.5b",
    "tinyllama:latest",
    "llama3.2:1b",
    "gemma3:1b",
    "llama3:8b",
    "phi3:mini"
]

def run_test(model_name):
    """Run a single test with specified model"""
    print(f"\n{'='*80}")
    print(f"Testing model: {model_name}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_API_URL}/run",
            data={
                "base_url": BASE_URL,
                "swagger": SWAGGER_URL,
                "api_key": API_KEY,
                "use_llm": "true",
                "llm_model": model_name,
                "reuse_tests": ""
            },
            timeout=600  # 10 minute timeout
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            return {
                "model": model_name,
                "status": "SUCCESS",
                "total_time": elapsed_time,
                "tests_generated": result.get("total_tests", 0),
                "tests_passed": result.get("passed", 0),
                "tests_failed": result.get("failed", 0),
                "error": None
            }
        else:
            return {
                "model": model_name,
                "status": "FAILED",
                "total_time": elapsed_time,
                "error": f"HTTP {response.status_code}: {response.text[:200]}"
            }
            
    except requests.exceptions.Timeout:
        return {
            "model": model_name,
            "status": "TIMEOUT",
            "total_time": 600,
            "error": "Request timed out after 10 minutes"
        }
    except Exception as e:
        return {
            "model": model_name,
            "status": "ERROR",
            "total_time": time.time() - start_time,
            "error": str(e)
        }

def main():
    print("\n" + "="*80)
    print("LLM BENCHMARK TEST")
    print(f"Testing {len(MODELS)} models")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = []
    
    for model in MODELS:
        result = run_test(model)
        results.append(result)
        
        # Print immediate result
        print(f"\nResult for {model}:")
        print(f"  Status: {result['status']}")
        print(f"  Total Time: {result['total_time']:.1f} seconds ({result['total_time']/60:.1f} minutes)")
        if result.get('tests_generated'):
            print(f"  Tests Generated: {result['tests_generated']}")
            print(f"  Tests Passed: {result['tests_passed']}")
            print(f"  Tests Failed: {result['tests_failed']}")
        if result.get('error'):
            print(f"  Error: {result['error']}")
        
        # Wait a bit between tests to let system stabilize
        if model != MODELS[-1]:
            print("\nWaiting 5 seconds before next test...")
            time.sleep(5)
    
    # Print summary
    print("\n" + "="*80)
    print("BENCHMARK SUMMARY")
    print("="*80)
    print(f"\n{'Model':<25} {'Status':<12} {'Time (s)':<12} {'Time (min)':<12} {'Tests':<8}")
    print("-" * 80)
    
    for result in results:
        status_emoji = {
            "SUCCESS": "✅",
            "FAILED": "❌",
            "TIMEOUT": "⏱️",
            "ERROR": "🔴"
        }.get(result['status'], "❓")
        
        print(f"{result['model']:<25} {status_emoji} {result['status']:<10} {result['total_time']:>10.1f}  {result['total_time']/60:>10.1f}  {result.get('tests_generated', 'N/A'):<8}")
    
    # Print ranking by speed
    successful = [r for r in results if r['status'] == 'SUCCESS']
    if successful:
        print("\n" + "="*80)
        print("RANKING BY SPEED (Successful runs only)")
        print("="*80)
        successful.sort(key=lambda x: x['total_time'])
        for i, result in enumerate(successful, 1):
            print(f"{i}. {result['model']:<25} {result['total_time']:>6.1f}s ({result['total_time']/60:.1f} min)")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"benchmark_results_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {results_file}")
    
    print("\n" + "="*80)
    print(f"Benchmark completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(f"{BASE_API_URL}/", timeout=5)
        if response.status_code != 200:
            print("⚠️  WARNING: Server may not be running properly")
    except:
        print("❌ ERROR: Cannot connect to server at http://127.0.0.1:8000")
        print("Please start the server first with: python -m uvicorn app:app --reload")
        exit(1)
    
    main()
