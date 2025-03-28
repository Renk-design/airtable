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
        return self.primitives_table.get_all()

    def get_semantic(self) -> List[Dict]:
        """Fetch all records from semantic table."""
        return self.semantic_table.get_all()

    def process_primitives(self, records: List[Dict]) -> Dict:
        """Process primitives records into brand-specific JSON structure."""
        primitives = {}
        for record in records:
            fields = record['fields']
            token = fields['Token']
            value = fields['Value']
            type_value = fields['Type']
            
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
            token = fields['Token']
            value = fields['Value']  # This links to primitive
            dark_value = fields['Dark_mode']
            type_value = fields['Type']
            
            # Create nested structure for both themes
            for theme, theme_value in [('light', value), ('dark', dark_value)]:
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
        # Fetch data
        primitives_records = self.get_primitives()
        semantic_records = self.get_semantic()

        # Process data
        primitives_data = self.process_primitives(primitives_records)
        semantic_data = self.process_semantic(semantic_records, primitives_data)

        # Save primitives
        self.save_json(primitives_data, 'primitives/brand1.json')

        # Save semantic
        for theme in ['light', 'dark']:
            self.save_json(
                semantic_data[theme],
                f'semantic/brand1/{theme}.json'
            )

if __name__ == "__main__":
    sync = TokenSync()
    sync.sync() 