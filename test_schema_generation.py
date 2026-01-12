"""
Test script to verify schema-based payload generation
"""
import json
from engine.swagger import load_swagger, get_request_body_schema, generate_sample_data, resolve_ref

# Load FakeStoreAPI Swagger
swagger_url = "http://127.0.0.1:8000/fakestoreapi_swagger.json"
print("Loading Swagger spec...")
swagger = load_swagger(swagger_url)
print(f"✓ Loaded Swagger spec\n")

# Test 1: Resolve schema reference
print("=" * 60)
print("TEST 1: Resolve Schema Reference")
print("=" * 60)
ref_path = "#/components/schemas/Pet"
schema = resolve_ref(swagger, ref_path)
print(f"Reference: {ref_path}")
print(f"Resolved Schema Keys: {list(schema.keys()) if schema else 'None'}")
print(f"✓ Schema resolved successfully\n")

# Test 2: Get request body schema for POST /pet
print("=" * 60)
print("TEST 2: Get Request Body Schema")
print("=" * 60)
path = "/pet"
method = "post"
request_schema = get_request_body_schema(swagger, path, method)
print(f"Endpoint: POST {path}")
print(f"Schema: {json.dumps(request_schema, indent=2)[:200]}...")
print(f"✓ Request body schema extracted\n")

# Test 3: Generate sample data for Pet schema
print("=" * 60)
print("TEST 3: Generate Sample Data")
print("=" * 60)
sample_data = generate_sample_data(swagger, request_schema)
print(f"Generated Sample Data:")
print(json.dumps(sample_data, indent=2))
print(f"✓ Sample data generated\n")

# Test 4: Test with rule-based generator
print("=" * 60)
print("TEST 4: Rule-Based Generator with Request Bodies")
print("=" * 60)
from engine.generator import generate_tests
tests = generate_tests(swagger)
print(f"Total tests generated: {len(tests)}")

# Find POST /pet tests
post_pet_tests = [t for t in tests if t['method'] == 'POST' and '/pet' in t['endpoint']]
if post_pet_tests:
    print(f"\nPOST /pet tests: {len(post_pet_tests)}")
    for test in post_pet_tests[:1]:  # Show first one
        print(f"\nTest: {test['test_name']}")
        print(f"Method: {test['method']}")
        print(f"Endpoint: {test['endpoint']}")
        if 'body' in test:
            print(f"Body: {json.dumps(test['body'], indent=2)[:300]}...")
            print("✓ Request body included!")
        else:
            print("✗ No request body found!")
else:
    print("✗ No POST /pet tests found")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
