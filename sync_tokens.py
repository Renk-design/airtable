import os
import json
from typing import Dict, List, Optional
from airtable import Airtable
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TokenSync:
    def __init__(self):
        self.base_id = os.getenv('AIRTABLE_BASE_ID')
        self.api_key = os.getenv('AIRTABLE_API_KEY')
        self.primitives_table = Airtable(self.base_id, 'primitives', self.api_key)
        self.semantic_table = Airtable(self.base_id, 'semantic', self.api_key)

    def get_primitives(self) -> List[Dict]:
        """Fetch all records from primitives table."""
        records = self.primitives_table.get_all()
        if records:
            print("Primitives record structure:", json.dumps(records[0], indent=2))
        return records

    def get_semantic(self) -> List[Dict]:
        """Fetch all records from semantic table."""
        records = self.semantic_table.get_all()
        if records:
            print("Semantic record structure:", json.dumps(records[0], indent=2))
        return records

    def process_primitives(self, records: List[Dict]) -> Dict:
        """Process primitives records into brand-specific JSON structure."""
        primitives = {}
        for record in records:
            fields = record['fields']
            
            # Only use required fields (lowercase)
            token = fields.get('token')
            value = fields.get('value')
            type_value = fields.get('type')
            
            if not all([token, value, type_value]):
                print(f"Warning: Skipping record with missing required fields: {fields}")
                continue
            
            # Create nested structure
            keys = token.split('-')
            current = primitives
            for key in keys[:-1]:
                current = current.setdefault(key, {})
            current[keys[-1]] = {
                "$type": type_value,
                "$value": value
            }
        return primitives

    def process_semantic(self, records: List[Dict], primitives: Dict) -> Dict:
        """Process semantic records into theme-specific JSON structure."""
        semantic = {
            'light': {},
            'dark': {}
        }
        
        for record in records:
            fields = record['fields']
            
            # Only use required fields (lowercase)
            token = fields.get('token')
            type_value = fields.get('type')
            light_value = fields.get('light')
            dark_value = fields.get('dark')
            
            if not all([token, type_value, light_value, dark_value]):
                print(f"Warning: Skipping record with missing required fields: {fields}")
                continue
            
            # Create nested structure for both themes
            for theme, theme_value in [('light', light_value), ('dark', dark_value)]:
                keys = token.split('-')
                current = semantic[theme]
                for key in keys[:-1]:
                    current = current.setdefault(key, {})
                current[keys[-1]] = {
                    "$type": type_value,
                    "$value": theme_value
                }
        
        return semantic

    def save_json(self, data: Dict, filepath: str):
        """Save data to JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def sync(self):
        """Main sync function to update all token files."""
        try:
            # Fetch data
            print("Fetching primitives records...")
            primitives_records = self.get_primitives()
            print(f"Found {len(primitives_records)} primitives records")
            
            print("Fetching semantic records...")
            semantic_records = self.get_semantic()
            print(f"Found {len(semantic_records)} semantic records")

            # Process data
            print("Processing primitives data...")
            primitives_data = self.process_primitives(primitives_records)
            
            print("Processing semantic data...")
            semantic_data = self.process_semantic(semantic_records, primitives_data)

            # Save primitives
            print("Saving primitives data...")
            self.save_json(primitives_data, 'primitives/brand1.json')

            # Save semantic
            print("Saving semantic data...")
            for theme in ['light', 'dark']:
                self.save_json(
                    semantic_data[theme],
                    f'semantic/brand1/{theme}.json'
                )
            
            print("Sync completed successfully!")
            
        except Exception as e:
            print(f"Error during sync: {str(e)}")
            raise

if __name__ == "__main__":
    sync = TokenSync()
    sync.sync() 