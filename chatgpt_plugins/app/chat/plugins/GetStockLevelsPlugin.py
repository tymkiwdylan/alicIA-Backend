from typing import Dict
import requests
from .plugin import PluginInterface

class GetStockLevelsPlugin(PluginInterface):

    def get_name(self) -> str:
        return "get_stock_levels"

    def get_description(self) -> str:
        return "Get the stock levels for a specific item by its ID via API."

    def get_parameters(self) -> Dict:
        """
        Return the parameters required for this plugin.
        In this case, there are two parameters: 'company_name' and 'item_id'.
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
                    "description": "the ID of the item to get stock levels for"
                }
            },
            "required": ["company_name", "item_id"]
            
        }
        
        return parameters

    def execute(self, **kwargs) -> Dict:
        company_name = kwargs['company_name']
        item_id = kwargs['item_id']

        # You can adjust the URL to match the actual API endpoint
        response = requests.get(f'http://127.0.0.1:5000/stock-levels/{item_id}', json={"company_name": company_name})

        if response.status_code == 200:
            return {"message": "success", "data": response.json().get('data')}, 200
        else:
            return {"message": "error", "data": None}, response.status_code
