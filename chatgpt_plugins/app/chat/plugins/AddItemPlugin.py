from typing import Dict
import requests
from .plugin import PluginInterface

class AddItemPlugin(PluginInterface):

    def get_name(self) -> str:
        return "add_item"

    def get_description(self) -> str:
        return "Add a new item to a company's inventory via API. Make sure you ask for all the parameters before executing."

    def get_parameters(self) -> Dict:
        """
        Return the parameters required for this plugin.
        In this case, there are three parameters: 'company_name', 'item', and 'quantity'.
        """
        parameters = {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "the name of the company"
                },
                "name": {
                    "type": "string",
                    "description": "the item to add"
                },
                "sku": {
                    "type": "string",
                    "description": "sku code for identification"
                },
                "description": {
                    "type": "string",
                    "description": "description of the item"
                    },
                "cost": {
                    "type": "number",
                    "description": "cost of the item"
                },
                "price": {
                    "type": "number",
                    "description": "price to the public"
                },
                "quantity": {
                    "type": "integer",
                    "description": "the quantity of the item to add"
                }
            }
        }
        
        return parameters

    def execute(self, **kwargs) -> Dict:
        company_name = kwargs['company_name']
        name = kwargs['name']
        sku = kwargs['sku']
        description = kwargs['description']
        cost = kwargs['cost']
        price = kwargs['price']
        quantity = kwargs['quantity']
        
        item = {
            'name': name,
            'sku': sku,
            'description': description,
            'cost': cost,
            'price': price
        }

        # Prepare the data to send in the POST request
        json_data = {
            "company_name": company_name,
            "item": item,
            "quantity": quantity
        }

        # You can adjust the URL to match the actual API endpoint
        response = requests.post('http://127.0.0.1:5000/items', json=json_data)

        if response.status_code == 201:
            return {"message": "success", "data": None}, 201
        else:
            return {"message": "error", "data": None}, response.status_code
