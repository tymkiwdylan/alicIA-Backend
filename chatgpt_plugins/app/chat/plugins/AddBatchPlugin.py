from typing import Dict
import requests
from .plugin import PluginInterface

class AddBatchPlugin(PluginInterface):

    def get_name(self) -> str:
        return "add_batch"

    def get_description(self) -> str:
        return "Add a new batch of items to a company's inventory via API."

    def get_parameters(self) -> Dict:
        """
        Return the parameters required for this plugin.
        In this case, there are two parameters: 'company_name' and 'batch'.
        """
        parameters = {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "the name of the company"
                },
                "batch_number" : {
                    "type": "string",
                    "description": "Unique batch number"
                },
                "item_id": {
                    "type": "string",
                    "description": "the id associated with the item"
                },
                "manufacturing_date": {
                    "type": "string",
                    "format": "date-time",
                    "description": "The exact date and time of manufacturing"
                },
                "expiry_date": {
                    "type": "string",
                    "format": "date-time",
                    "description": "date when the batch expires"
                },
                "quantity": {
                    "type": "number",
                    "description": "Total quantity of items in the batch",
                },
                "current_stock": {
                    "type": "number",
                    "description": "Current stock level of items in this batch"
                },
                "location_id":{
                    "type": "string",
                    "description": "Reference to the location of the batch"
                },
                "status": {
                    "type": "string",
                    "enum": ["In Stock", "Sold", "Expired"]
                }
            },
            "required": ["company_name", "batch_number", "item_id", "quantity"]
        }
        
        return parameters

    def execute(self, **kwargs) -> Dict:
        company_name = kwargs['company_name']
        batch = {
            "batch_number": kwargs['batch_number'],
            "item_id": kwargs['item_id'],
            "manufacturing_date": kwargs.get('manufacturing_date', ''),
            "expiry_date": kwargs.get('expiry_date', ''),
            "quantity": kwargs['quantity'],
            "current_stock": kwargs.get('current_stock', kwargs['quantity']),  # Optional parameter
            "location_id": kwargs.get('location_id', ''),      # Optional parameter
            "status": kwargs.get('status', 'In Stock')         # Optional parameter
        }

        # Prepare the data to send in the POST request
        json_data = {
            "company_name": company_name,
            "batch": batch
        }

        # You can adjust the URL to match the actual API endpoint
        response = requests.post('http://127.0.0.1:5000/batches', json=json_data)

        if response.status_code == 201:
            return {"message": "success", "data": None}, 201
        else:
            return {"message": "error", "data": None}, response.status_code
