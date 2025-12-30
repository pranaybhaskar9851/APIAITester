# Updated Test Generation Strategy

## Overview
Changed from simple auth-based tests to **intelligent context-aware test scenarios** that better validate API behavior.

## Old Strategy (❌ Removed)
Every endpoint got the same 2 tests:
1. Valid auth test (200)
2. Invalid auth test (401)

**Problem:** Not realistic. POST/PUT/DELETE/PATCH need input validation testing, not just auth testing.

## New Strategy (✅ Implemented)

### GET Endpoints
**Test 1:** Valid Request (200)
- Proper authentication
- Valid parameters
- Expected: Successful response

**Test 2:** Unauthorized (401)
- Invalid/missing authentication
- Expected: Access denied

**Example:**
```json
// Test 1: Valid
{
  "test_name": "GET /pet/findByStatus - Valid Request",
  "method": "GET",
  "endpoint": "/pet/findByStatus?status=available",
  "expected_status": 200,
  "auth": "valid"
}

// Test 2: Unauthorized
{
  "test_name": "GET /pet/findByStatus - Unauthorized",
  "method": "GET",
  "endpoint": "/pet/findByStatus?status=available",
  "expected_status": 401,
  "auth": "invalid"
}
```

### POST Endpoints
**Test 1:** Valid Request (201)
- Valid authentication
- Valid request body with proper data
- Expected: Resource created successfully

**Test 2:** Invalid Input (400)
- Valid authentication (not an auth test!)
- Invalid request body (empty name, invalid ID like -1)
- Expected: Bad request error

**Example:**
```json
// Test 1: Valid
{
  "test_name": "POST /pet - Valid Request",
  "method": "POST",
  "endpoint": "/pet",
  "expected_status": 201,
  "auth": "valid",
  "body": {
    "id": 10,
    "name": "doggie",
    "photoUrls": ["string"]
  }
}

// Test 2: Invalid Input
{
  "test_name": "POST /pet - Invalid Input",
  "method": "POST",
  "endpoint": "/pet",
  "expected_status": 400,
  "auth": "valid",
  "body": {
    "id": -1,        // ❌ Invalid ID
    "name": "",      // ❌ Empty name
    "photoUrls": ["string"]
  }
}
```

### PUT Endpoints
**Test 1:** Valid Request (200)
- Valid authentication
- Valid resource ID (e.g., /pet/1)
- Valid request body
- Expected: Resource updated successfully

**Test 2:** Non-Existent Resource (404)
- Valid authentication (not an auth test!)
- Non-existent resource ID (e.g., /pet/999999)
- Valid request body
- Expected: Resource not found

**Example:**
```json
// Test 1: Valid
{
  "test_name": "PUT /pet - Valid Request",
  "method": "PUT",
  "endpoint": "/pet",
  "expected_status": 200,
  "auth": "valid",
  "body": {
    "id": 1,
    "name": "updated-doggie"
  }
}

// Test 2: Non-Existent Resource
{
  "test_name": "PUT /pet/{petId} - Invalid Input",
  "method": "PUT",
  "endpoint": "/pet/999999",  // ❌ Doesn't exist
  "expected_status": 404,
  "auth": "valid",
  "body": {
    "id": 999999,
    "name": "test"
  }
}
```

### DELETE Endpoints
**Test 1:** Valid Request (200)
- Valid authentication
- Valid resource ID (e.g., /pet/1)
- Expected: Resource deleted successfully

**Test 2:** Non-Existent Resource (404)
- Valid authentication (not an auth test!)
- Non-existent resource ID (e.g., /pet/999999)
- Expected: Resource not found

**Example:**
```json
// Test 1: Valid
{
  "test_name": "DELETE /pet/{petId} - Valid Request",
  "method": "DELETE",
  "endpoint": "/pet/1",
  "expected_status": 200,
  "auth": "valid"
}

// Test 2: Non-Existent Resource
{
  "test_name": "DELETE /pet/{petId} - Invalid Input",
  "method": "DELETE",
  "endpoint": "/pet/999999",  // ❌ Doesn't exist
  "expected_status": 404,
  "auth": "valid"
}
```

## Implementation Details

### Rule-Based Generator (generator.py)
```python
# Create negative test based on method type
if method.lower() == 'get':
    # For GET: test unauthorized access
    negative_test = {..., "expected_status": 401, "auth": "invalid"}
else:
    # For POST/PUT/DELETE/PATCH: test with invalid/non-existent resource
    invalid_endpoint = endpoint.replace("/1", "/999999")
    negative_test = {
        ...,
        "expected_status": 404 if method.lower() in ['put', 'delete'] else 400,
        "auth": "valid"
    }
    
    # Add invalid body for POST
    if method.lower() == 'post':
        invalid_body = {"id": -1, "name": ""}
        negative_test["body"] = invalid_body
```

### LLM Generator (llm_generator.py)
Updated prompt with clear instructions:
```
For EACH endpoint, generate ONLY these 2 tests:
1. Valid positive test (status 200 or 201 for POST)
2. Negative test:
   - GET: Unauthorized test (status 401, auth="invalid")
   - POST/PUT/DELETE/PATCH: Invalid input test (status 404 or 400, use non-existent ID like 999999)

Rules:
- Replace {param} with "1" for valid test, "999999" for invalid test
- For invalid input tests on POST: use invalid body data (empty name, invalid id: -1)
```

## Verification

Run the verification script:
```bash
python test_new_strategy.py
```

**Results:**
```
✓ GET endpoints: Valid + Unauthorized tests
✓ POST endpoints: Valid + Invalid input tests (id=-1, name='')
✓ PUT endpoints: Valid + Non-existent resource tests (404)
✓ DELETE endpoints: Valid + Non-existent resource tests (404)
```

## Benefits

✅ **More Realistic:** Tests actual API behavior, not just authentication  
✅ **Better Coverage:** Validates input handling and error responses  
✅ **Catches Real Bugs:** Finds validation errors, missing resources  
✅ **Follows Best Practices:** Tests positive and negative scenarios per method type  
✅ **Smarter Testing:** Context-aware based on HTTP method  

## Impact

**Before:**
- 38 tests: 19 valid + 19 unauthorized
- All POST/PUT/DELETE tests just checked auth
- No input validation testing

**After:**
- 38 tests: 19 valid + 19 context-aware negative tests
- GET: 8 valid + 8 unauthorized = 16 tests
- POST: 6 valid + 6 invalid input = 12 tests
- PUT: 2 valid + 2 not found = 4 tests
- DELETE: 3 valid + 3 not found = 6 tests

**Test failures should now reveal actual API issues, not just missing authentication!**
