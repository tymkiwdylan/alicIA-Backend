from typing import Dict
import requests
from .plugin import PluginInterface

class DeleteSupplierPlugin(PluginInterface):

    def get_name(self) -> str:
        return "delete_supplier"

    def get_description(self) -> str:
        return "Delete a specific supplier by its ID via API. ASK FOR CONFIRMATION BEFORE EXECUTING"

    def get_parameters(self) -> Dict:
        """
        Return the parameters required for this plugin.
        In this case, there are two parameters: 'company_name' and 'supplier_id'.
        """
        parameters = {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "the name of the company"
                },
                "supplier_id": {
                    "type": "string",
                    "description": "ID of the supplier to delete"
                }
            },
            "required": ["company_name", "supplier_id"]
        }
        
        return parameters

    def execute(self, **kwargs) -> Dict:
        company_name = kwargs['company_name']
        supplier_id = kwargs['supplier_id']

        # Prepare the data to send in the DELETE request
        json_data = {
            "company_name": company_name
        }

        # You can adjust the URL to match the actual API endpoint
        response = requests.delete(f'http://127.0.0.1:5000/suppliers/{supplier_id}', json=json_data)

        if response.status_code == 200:
            return {"message": "success", "data": None}, 200
        elif response.status_code == 404:
            return {"message": "error", "data": "Supplier not found"}, 404
        else:
            return {"message": "error", "data": None}, response.status_code
