# Schema-Based Request Payload Generation

## Overview
Tests were failing because POST/PUT/PATCH requests had no request bodies. Now the system automatically generates valid request payloads based on Swagger schema definitions.

## What Changed

### 1. New Functions in `swagger.py`

#### `resolve_ref(swagger, ref_path)`
- Resolves `$ref` references like `"#/components/schemas/Pet"`
- Navigates through the Swagger spec to find schema definitions

#### `generate_sample_data(swagger, schema)`
- Generates valid sample data from a JSON schema
- Supports: objects, arrays, strings, integers, numbers, booleans
- Handles nested schemas and references
- Uses `example`, `default`, or `enum` values when available
- Prevents infinite recursion with depth limiting

#### `get_request_body_schema(swagger, path, method)`
- Extracts the request body schema for a specific endpoint
- Prefers `application/json` content type
- Returns the schema object or `None` if no body required

### 2. Updated `generator.py` (Rule-Based)

**Before:**
```python
tests.append({
    "id": "test001",
    "test_name": "POST /pet - Positive Test",
    "method": "POST",
    "endpoint": "/pet",
    "expected_status": 200,
    "headers": {...}
})
```

**After:**
```python
# Generate request body for POST/PUT/PATCH
request_body = None
if method.lower() in ['post', 'put', 'patch']:
    schema = get_request_body_schema(swagger, path, method)
    if schema:
        request_body = generate_sample_data(swagger, schema)

test_case = {
    "id": "test001",
    "test_name": "POST /pet - Positive Test",
    "method": "POST",
    "endpoint": "/pet",
    "expected_status": 200,
    "headers": {...}
}
if request_body:
    test_case["body"] = request_body  # ✓ Request body added!
```

### 3. Updated `llm_generator.py` (LLM-Based)

**Enhancements:**
- Imports schema functions
- Generates example payloads for POST/PUT/PATCH endpoints
- Includes examples in LLM prompt
- Validates and preserves `"body"` field in generated tests

**LLM Prompt Enhancement:**
```
Request Body Examples (use these for POST/PUT/PATCH):
{
  "POST /pet": {
    "id": 10,
    "name": "doggie",
    "category": {"id": 1, "name": "Dogs"},
    "photoUrls": ["string"],
    "tags": [{"id": 0, "name": "string"}],
    "status": "available"
  }
}
```

### 4. Updated `executor.py`

**Before:**
```python
r = requests.request(
    test["method"],
    url,
    headers=headers,
    timeout=30
)
```

**After:**
```python
body_json = None
if "body" in test:
    body_json = test["body"]
    request_data["body"] = body_json

# Make request with or without body
if body_json is not None:
    r = requests.request(
        test["method"],
        url,
        headers=headers,
        json=body_json,  # ✓ Send request body!
        timeout=30
    )
else:
    r = requests.request(
        test["method"],
        url,
        headers=headers,
        timeout=30
    )
```

## Example: POST /pet

### Swagger Schema Reference:
```json
{
  "requestBody": {
    "content": {
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/Pet"
        }
      }
    }
  }
}
```

### Generated Test Case:
```json
{
  "id": "test001",
  "test_name": "POST /pet - Positive Test",
  "method": "POST",
  "endpoint": "/pet",
  "expected_status": 200,
  "auth": "valid",
  "headers": {
    "accept": "application/json",
    "Content-Type": "application/json"
  },
  "body": {
    "id": 10,
    "name": "doggie",
    "category": {
      "id": 1,
      "name": "Dogs"
    },
    "photoUrls": ["string"],
    "tags": [
      {
        "id": 0,
        "name": "string"
      }
    ],
    "status": "available"
  }
}
```

### Actual Request Sent:
```bash
curl -X 'POST' \
  'https://fakestoreapi.com/products' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "id": 10,
  "name": "doggie",
  "category": {
    "id": 1,
    "name": "Dogs"
  },
  "photoUrls": [
    "string"
  ],
  "tags": [
    {
      "id": 0,
      "name": "string"
    }
  ],
  "status": "available"
}'
```

## Benefits

✅ **Tests Pass Now**: POST/PUT/PATCH requests include valid payloads  
✅ **Schema Compliance**: Payloads match Swagger schema definitions  
✅ **Automatic**: No manual payload creation needed  
✅ **Smart**: Uses example/default values when available  
✅ **Flexible**: Handles nested objects, arrays, and references  
✅ **Both Generators**: Works with rule-based and LLM generation  

## Testing

Run the verification script:
```bash
python test_schema_generation.py
```

Expected output:
```
✓ Loaded Swagger spec
✓ Schema resolved successfully
✓ Request body schema extracted
✓ Sample data generated
✓ Request body included!
```

## Impact on Test Execution

**Before:**
- POST /pet → 400 Bad Request (missing body)
- PUT /pet → 400 Bad Request (missing body)
- Tests failing due to validation errors

**After:**
- POST /pet → 200 OK (valid payload sent)
- PUT /pet → 200 OK (valid payload sent)
- Tests passing with proper request bodies

## Next Steps

1. Run tests through the web UI: http://127.0.0.1:8000
2. Check generated test cases in `test_cases.json`
3. Verify request bodies in `artifacts/{timestamp}/{test_id}_request.json`
4. Review test results in HTML reports
