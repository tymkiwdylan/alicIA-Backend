from typing import Dict
import requests
from .plugin import PluginInterface

class UpdateBatchPlugin(PluginInterface):

    def get_name(self) -> str:
        return "update_batch"

    def get_description(self) -> str:
        return "Update information about a specific batch by its ID via API."

    def get_parameters(self) -> Dict:
        """
        Return the parameters required for this plugin.
        In this case, there are three parameters: 'company_name', 'batch_id', and 'batch_data'.
        """
        parameters = {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "the name of the company"
                },
                "batch_id": {
                    "type": "string",
                    "description": "ID of the batch to update"
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
            "required": ["company_name", "batch_id"]
        }
        
        return parameters

    def execute(self, **kwargs) -> Dict:
        company_name = kwargs['company_name']
        batch_id = kwargs['batch_id']
        
        batch_data = {}
        if 'batch_number' in kwargs:
            batch_data['batch_number'] = kwargs['batch_number']
        if 'manufacturing_date' in kwargs:
            batch_data['manufacturing_date'] = kwargs['manufacturing_date']
        if 'expiry_date' in kwargs:
            batch_data['expiry_date'] = kwargs['expiry_date']
        if 'quantity' in kwargs:
            batch_data['quantity'] = kwargs['quantity']
        if 'current_stock' in kwargs:
            batch_data['current_stock'] = kwargs['current_stock']
        if 'location_id' in kwargs:
            batch_data['location_id'] = kwargs['location_id']
        if 'status' in kwargs:
            batch_data['status'] = kwargs['status']

        # Prepare the data to send in the PUT request
        json_data = {
            "company_name": company_name,
            "batch": batch_data
        }

        # You can adjust the URL to match the actual API endpoint
        response = requests.put(f'http://127.0.0.1:5000/batches/{batch_id}', json=json_data)

        if response.status_code == 200:
            return {"message": "success", "data": None}, 200
        elif response.status_code == 404:
            return {"message": "error", "data": "Batch not found"}, 404
        else:
            return {"message": "error", "data": None}, response.status_code
