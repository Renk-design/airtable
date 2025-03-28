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

# Load issue data (raw text from GitHub issue)
with open("issue.json", "r") as f:
    issue_data = f.read().strip()

# Split the incoming data
token, value, type_value = issue_data.split(",")

# Convert token to nested dictionary
keys = token.split("-")
insert_or_update_nested(nested_json, keys, type_value, value)

# Save the updated JSON
with open("primitives.json", "w") as f:
    json.dump(nested_json, f, indent=4)

print("primitives.json updated successfully!")
