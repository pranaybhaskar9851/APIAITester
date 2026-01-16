import json
from engine.swagger import load_swagger

swagger_file = "c:\\Users\\ppagadala\\OneDrive - OpenText\\Documents\\BIRT\\26.1\\Hackathon\\new\\api-ai-tester-v001\\docs-data.json"
spec = load_swagger(swagger_file)

paths = spec.get('paths', {})
print(f"\n=== Analyzing OpenAPI Spec ===")
print(f"Total paths: {len(paths)}\n")

method_count = {}
for path, methods in paths.items():
    print(f"\n{path}:")
    for method in methods.keys():
        method_lower = method.lower()
        if method_lower in ["get", "post", "put", "delete", "patch"]:
            print(f"  ✓ {method.upper()}")
            method_count[method.upper()] = method_count.get(method.upper(), 0) + 1
        else:
            print(f"  ✗ {method.upper()} (skipped - not a test method)")

print(f"\n=== Summary ===")
for method, count in sorted(method_count.items()):
    print(f"{method}: {count} endpoints")
