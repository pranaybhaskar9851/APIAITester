"""
Test the JSON repair function
"""
import re

def fix_json_format(json_str):
    """
    Fix common JSON formatting issues from LLM output.
    Converts JavaScript-style syntax to valid JSON.
    """
    # Remove template literals and replace with empty strings or actual values
    json_str = re.sub(r'`([^`]*)`', r'"\1"', json_str)  # Replace backticks with double quotes
    
    # Fix template variable references like ${endpoint}
    json_str = re.sub(r'\$\{[^}]+\}', '""', json_str)
    
    # Fix unquoted property names (JavaScript style)
    # Match word characters followed by colon (not already quoted)
    json_str = re.sub(r'(\s+)(\w+)(:)', r'\1"\2"\3', json_str)
    
    # Fix unquoted single word values (like: endpoint,)
    # Match unquoted words that are values (after colon, before comma/brace)
    json_str = re.sub(r':\s*(\w+)\s*([,}])', r': "\1"\2', json_str)
    
    # Replace single quotes with double quotes
    json_str = json_str.replace("'", '"')
    
    # Remove trailing commas before closing brackets/braces
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    
    return json_str

# Test with the problematic output from the error
bad_json = """[
  {
    id: 'test001',
    test_name: `GET ${endpoint} - Valid`,
    method: 'GET',
    endpoint,
    expected_status: 200,
    auth: 'valid',
    headers: { accept: 'application/json' }
  },
  {
    id: 'test002',
    test_name: `GET ${endpoint} - Unauthorized`,
    method: 'GET',
    endpoint,
    expected_status: 401,
    auth: 'invalid',
    headers: { accept: 'application/json' }
  }
]"""

print("ORIGINAL (BAD):")
print(bad_json)
print("\n" + "="*70 + "\n")

fixed = fix_json_format(bad_json)
print("FIXED:")
print(fixed)
print("\n" + "="*70 + "\n")

# Try to parse it
import json
try:
    parsed = json.loads(fixed)
    print("✓ JSON PARSING SUCCESSFUL!")
    print(f"Parsed {len(parsed)} test objects")
    print("\nFirst test:")
    print(json.dumps(parsed[0], indent=2))
except json.JSONDecodeError as e:
    print(f"✗ JSON PARSING FAILED: {e}")
    print(f"Error at position {e.pos}")
