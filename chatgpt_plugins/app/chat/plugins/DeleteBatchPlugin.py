from typing import Dict
import requests
from .plugin import PluginInterface

class DeleteBatchPlugin(PluginInterface):

    def get_name(self) -> str:
        return "delete_batch"

    def get_description(self) -> str:
        return "Delete a specific batch by its ID via API. ASK FOR CONFIRMATION"

    def get_parameters(self) -> Dict:
        """
        Return the parameters required for this plugin.
        In this case, there are two parameters: 'company_name' and 'batch_id'.
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
                    "description": "ID of the batch to delete"
                }
            },
            "required": ["company_name", "batch_id"]
        }
        
        return parameters

    def execute(self, **kwargs) -> Dict:
        company_name = kwargs['company_name']
        batch_id = kwargs['batch_id']

        # Prepare the data to send in the DELETE request
        json_data = {
            "company_name": company_name
        }

        # You can adjust the URL to match the actual API endpoint
        response = requests.delete(f'http://127.0.0.1:5000/batches/{batch_id}', json=json_data)

        if response.status_code == 200:
            return {"message": "success", "data": None}, 200
        elif response.status_code == 404:
            return {"message": "error", "data": "Batch not found"}, 404
        else:
            return {"message": "error", "data": None}, response.status_code
