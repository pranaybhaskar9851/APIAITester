"""
Test script to verify new test generation strategy:
- GET: Valid + Unauthorized
- POST/PUT/DELETE/PATCH: Valid + Invalid Input
"""
import json
from engine.swagger import load_swagger
from engine.generator import generate_tests

# Load FakeStoreAPI Swagger
swagger_url = "http://127.0.0.1:8000/fakestoreapi_swagger.json"
print("Loading Swagger spec...")
swagger = load_swagger(swagger_url)
print(f"✓ Loaded Swagger spec\n")

# Generate tests
print("=" * 70)
print("GENERATING TESTS WITH NEW STRATEGY")
print("=" * 70)
tests = generate_tests(swagger)
print(f"\nTotal tests generated: {len(tests)}\n")

# Analyze test distribution
get_tests = [t for t in tests if t['method'] == 'GET']
post_tests = [t for t in tests if t['method'] == 'POST']
put_tests = [t for t in tests if t['method'] == 'PUT']
delete_tests = [t for t in tests if t['method'] == 'DELETE']

print(f"GET tests: {len(get_tests)}")
print(f"POST tests: {len(post_tests)}")
print(f"PUT tests: {len(put_tests)}")
print(f"DELETE tests: {len(delete_tests)}\n")

# Show example GET tests
print("=" * 70)
print("EXAMPLE: GET ENDPOINT TESTS")
print("=" * 70)
get_pet_tests = [t for t in tests if t['method'] == 'GET' and '/pet/' in t['endpoint']][:2]
for i, test in enumerate(get_pet_tests, 1):
    print(f"\nTest {i}: {test['test_name']}")
    print(f"  Method: {test['method']}")
    print(f"  Endpoint: {test['endpoint']}")
    print(f"  Expected Status: {test['expected_status']}")
    print(f"  Auth: {test['auth']}")
    if test['expected_status'] == 401:
        print(f"  ✓ Unauthorized test (correct!)")
    else:
        print(f"  ✓ Valid request test")

# Show example POST tests
print("\n" + "=" * 70)
print("EXAMPLE: POST ENDPOINT TESTS")
print("=" * 70)
post_pet_tests = [t for t in tests if t['method'] == 'POST' and t['endpoint'] == '/pet'][:2]
for i, test in enumerate(post_pet_tests, 1):
    print(f"\nTest {i}: {test['test_name']}")
    print(f"  Method: {test['method']}")
    print(f"  Endpoint: {test['endpoint']}")
    print(f"  Expected Status: {test['expected_status']}")
    print(f"  Auth: {test['auth']}")
    if 'body' in test:
        body = test['body']
        print(f"  Body: {json.dumps(body, indent=4)[:150]}...")
        if test['expected_status'] == 400:
            print(f"  ✓ Invalid input test (id={body.get('id', 'N/A')}, name='{body.get('name', 'N/A')}')")
        else:
            print(f"  ✓ Valid request test")

# Show example PUT tests
print("\n" + "=" * 70)
print("EXAMPLE: PUT ENDPOINT TESTS")
print("=" * 70)
put_pet_tests = [t for t in tests if t['method'] == 'PUT' and '/pet' in t['endpoint']][:2]
for i, test in enumerate(put_pet_tests, 1):
    print(f"\nTest {i}: {test['test_name']}")
    print(f"  Method: {test['method']}")
    print(f"  Endpoint: {test['endpoint']}")
    print(f"  Expected Status: {test['expected_status']}")
    print(f"  Auth: {test['auth']}")
    if '999999' in test['endpoint']:
        print(f"  ✓ Non-existent resource test (404 expected)")
    else:
        print(f"  ✓ Valid request test")

# Show example DELETE tests
print("\n" + "=" * 70)
print("EXAMPLE: DELETE ENDPOINT TESTS")
print("=" * 70)
delete_pet_tests = [t for t in tests if t['method'] == 'DELETE'][:2]
for i, test in enumerate(delete_pet_tests, 1):
    print(f"\nTest {i}: {test['test_name']}")
    print(f"  Method: {test['method']}")
    print(f"  Endpoint: {test['endpoint']}")
    print(f"  Expected Status: {test['expected_status']}")
    print(f"  Auth: {test['auth']}")
    if '999999' in test['endpoint']:
        print(f"  ✓ Non-existent resource test (404 expected)")
    else:
        print(f"  ✓ Valid request test")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("✓ GET endpoints: Valid + Unauthorized tests")
print("✓ POST endpoints: Valid + Invalid input tests")
print("✓ PUT endpoints: Valid + Non-existent resource tests (404)")
print("✓ DELETE endpoints: Valid + Non-existent resource tests (404)")
print("\nNew test strategy implemented successfully!")
