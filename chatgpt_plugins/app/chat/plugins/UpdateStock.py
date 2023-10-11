from typing import Dict
import requests
from .plugin import PluginInterface

class UpdateStockLevelPlugin(PluginInterface):

    def get_name(self) -> str:
        return "update_stock_level"

    def get_description(self) -> str:
        return "Update the stock level for a specific item by its ID via API."

    def get_parameters(self) -> Dict:
        """
        Return the parameters required for this plugin.
        In this case, there are three parameters: 'company_name', 'item_id', and 'new_level'.
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
                    "description": "the ID of the item to update stock levels for"
                },
                "new_level": {
                    "type": "number",
                    "description": "the new stock level for the item"
                }
            },
            "required": ["company_name", "item_id", "new_level"]
        }
        
        return parameters

    def execute(self, **kwargs) -> Dict:
        company_name = kwargs['company_name']
        item_id = kwargs['item_id']
        new_level = kwargs['new_level']

        # Prepare the data to send in the PUT request
        json_data = {
            "company_name": company_name,
            "new_level": new_level
        }

        # You can adjust the URL to match the actual API endpoint
        response = requests.put(f'http://127.0.0.1:5000/stock-levels/{item_id}', json=json_data)

        if response.status_code == 200:
            return {"message": "success", "data": None}, 200
        else:
            return {"message": "error", "data": None}, response.status_code
