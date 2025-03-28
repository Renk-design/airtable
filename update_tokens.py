import json
import os

def insert_or_update_nested(d, keys, type_value, value):
    """Recursively inserts or updates keys in the dictionary to create or modify a nested structure."""
    key = keys.pop(0)
    if not keys:
        # If the key exists, update its value; if not, create a new one
        if key in d:
            d[key]["$type"] = type_value
            d[key]["$value"] = value
        else:
            d[key] = {"$type": type_value, "$value": value}
    else:
        d.setdefault(key, {})
        insert_or_update_nested(d[key], keys, type_value, value)

# Check if the primitives.json file exists
if os.path.exists("primitives.json"):
    # Load the existing JSON file
    with open("primitives.json", "r") as f:
        nested_json = json.load(f)
else:
    # If the file doesn't exist, initialize an empty dictionary
    nested_json = {}

# Load aggregated issue data
with open("issues.json", "r") as f:
    issue_lines = f.readlines()

for issue_data in issue_lines:
    issue_data = issue_data.strip()
    if not issue_data:  # Skip empty lines
        continue

    # Split the incoming data
    try:
        token, value, type_value = issue_data.split(",")
        keys = token.split("-")
        insert_or_update_nested(nested_json, keys, type_value, value)
    except ValueError:
        print(f"Skipping malformed issue data: {issue_data}")
        continue

# Save the updated JSON
with open("primitives.json", "w") as f:
    json.dump(nested_json, f, indent=4)

print("primitives.json updated successfully!")
