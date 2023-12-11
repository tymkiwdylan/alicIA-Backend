from typing import Dict
import requests
from .plugin import PluginInterface

class UpdateItemPlugin(PluginInterface):

    def get_name(self) -> str:
        return "update_item"

    def get_description(self) -> str:
        return "Update information about a specific item by its ID via API. If you don't have the item_id, it appears as $oid when you call get_items"

    def get_parameters(self) -> Dict:
        """
        Return the parameters required for this plugin.
        In this case, there are three parameters: 'company_name', 'item_id', and 'item_data'.
        """
        parameters = {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "the name of the company"
                },
                "item_id": {
                    "type": "string",
                    "format": "ObjectID",
                    "description": "the ID of the item to update"
                },
                "name": {
                    "type": "string",
                    "description": "the updated name"
                },
                "sku": {
                    "type": "string",
                    "description": "then new sku"
                },
                "description": {
                    "type": "string",
                    "description": "New description of the item"
                },
                "cost": {
                    "type": "number",
                    "description": "new cost of the item"
                },
                "price": {
                    "oneOf": [{
                        "type": "number",
                        "description": "new price to the public"
                        },
                        {
                        "type": "string",
                        "pattern": "^[0-9]+(\\s*[\\+\\-\\*/]\\s*[0-9]+)*$",
                        "description": "A mathematical expression consisting of numbers and basic operators"
                        }      
                    ]
                }    
            },
            "required": ["company_name", "item_id"]
        }
        
        return parameters

    def execute(self, **kwargs) -> Dict:
        allowed_chars = set('0123456789.+-*/ ')
        company_name = kwargs.get('company_name', None)
        item_id = kwargs.get('item_id', None)
        
        if type(kwargs['price']) == 'string':
            kwargs['price'] = eval(kwargs['price'])
        
        item_data = {}
        if 'name' in kwargs:
            item_data['name'] = kwargs['name']
        if 'sku' in kwargs:
            item_data['sku'] = kwargs['sku']
        if 'description' in kwargs:
            item_data['description'] = kwargs['description']
        if 'cost' in kwargs:
            item_data['cost'] = kwargs['cost']
        if 'price' in kwargs:
            item_data['price'] = kwargs['price']

        if company_name is None or item_id is None:
            return {"message": "error", "data": "Missing required parameters"}, 400

        # Prepare the data to send in the PUT request
        json_data = {
            "company_name": company_name,
            "item": item_data
        }
        

        # You can adjust the URL to match the actual API endpoint
        response = requests.put(f'http://127.0.0.1:5000/items/{item_id}', json=json_data)

        if response.status_code == 200:
            return {"message": "success", "data": None}, 200
        elif response.status_code == 404:
            return {"message": "error", "data": "Object not found"}, 404
        else:
            print(response)
            return {"message": response.json(), "data": None}, response.status_code

