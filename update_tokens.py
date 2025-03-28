import json

def insert_nested(d, keys, type_value, value):
    """Recursively inserts keys into dictionary to create a nested structure."""
    key = keys.pop(0)
    if not keys:
        d[key] = {"$type": type_value, "$value": value}
    else:
        d.setdefault(key, {})
        insert_nested(d[key], keys, type_value, value)

# Load issue data (raw text from GitHub issue)
with open("issue.json", "r") as f:
    issue_data = f.read().strip()

# Split the incoming data
token, value, type_value = issue_data.split(",")

# Convert token to nested dictionary
keys = token.split("-")
nested_json = {}
insert_nested(nested_json, keys, type_value, value)

# Save the structured JSON
with open("primitives.json", "w") as f:
    json.dump(nested_json, f, indent=4)

print("tokens.json updated successfully!")
