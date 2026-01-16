import json

with open('docs-data.json', encoding='utf-8') as f:
    spec = json.load(f)

paths = spec.get('paths', {})
print(f"Total paths: {len(paths)}\n")

for path, methods in paths.items():
    print(f"\n{path}:")
    for method in methods:
        if method.lower() in ["get", "post", "put", "delete", "patch"]:
            print(f"  - {method.upper()}")
