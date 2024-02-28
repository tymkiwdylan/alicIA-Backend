from typing import Dict
import requests
from .plugin import PluginInterface

class LogStockMovementPlugin(PluginInterface):

    def get_name(self) -> str:
        return "log_stock_movement"

    def get_description(self) -> str:
        return "Log a stock movement for a specific company via API."

    def get_parameters(self) -> Dict:
        """
        Return the parameters required for this plugin.
        In this case, there are two parameters: 'company_name' and 'movement'.
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
                    "description": "the id of the item"
                },
                "quantity": {
                    "type": "number",
                    "description": "The quantity of items"
                },
                "movement_type": {
                    "type": "string",
                    "enum": ["Recieved", "Sold", "Disposed", "Returned", "Adjustment", "Promotion", "Expired", "Lost"],
                    "description": "The type of movement to be recorded"
                },
                "supplier_name": {
                    "type": "string",
                    "description": "name of the supplier"
                },
                "description": {
                    "type": "string",
                    "description": "Short description of the movement"
                } 
                
            },
            "required": ["company_name", "item_id", "quantity", "movement_type"]
            
        }
        
        return parameters

    def execute(self, **kwargs) -> Dict:
        
        company_name = kwargs['company_name']
        item_id = kwargs['item_id']
        quantity = kwargs['quantity']
        movement_type = kwargs['movement_type']
        supplier_name = kwargs.get('supplier_name', None)  # Optional parameter
        description = kwargs.get('description', None)  # Optional parameter

        # Construct the movement dictionary
        movement = {
            "item_id": item_id,
            "quantity": quantity,
            "movement_type": movement_type,
            "supplier_name": supplier_name,
            "description": description
        }
        
        json_data = {
            "company_name": company_name,
            "movement": movement
        }


        # You can adjust the URL to match the actual API endpoint
        response = requests.post('http://127.0.0.1:5000/stock-movements', json=json_data)

        if response.status_code == 201:
            return {"message": "success", "data": None}, 201
        else:
            return {"message": "error", "data": None}, response.status_code
