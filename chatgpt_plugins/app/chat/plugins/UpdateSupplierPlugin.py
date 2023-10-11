from typing import Dict
import requests
from .plugin import PluginInterface

class UpdateSupplierPlugin(PluginInterface):

    def get_name(self) -> str:
        return "update_supplier"

    def get_description(self) -> str:
        return "Update information about a specific supplier by its ID via API."

    def get_parameters(self) -> Dict:
        """
        Return the parameters required for this plugin.
        In this case, there are three parameters: 'company_name', 'supplier_id', and 'supplier_data'.
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
                    "description": "id of the supplier"
                },
                "supplier": {
                    "type": "string",
                    "description": "the supplier name"
                },
                "email": {
                    "type": "string",
                    "description": "email of the supplier"
                },
                "phone_number":{
                    "type": "string",
                    "description": "Phhone number to contact the supplier"
                },
                "items": {
                    "type": "array",
                    "items":{
                        "type": "string",
                        "description": "id associated with the item"
                    },
                    "description": "list of the ids of items they supply"
                }
            },
            "required": ["company_name", "supplier_id"]
        }
        
        return parameters

    def execute(self, **kwargs) -> Dict:
        company_name = kwargs['company_name']
        supplier_id = kwargs['supplier_id']
        
        supplier_data = {}
        if 'name' in kwargs:
            supplier_data['name'] = kwargs['supplier']
        if 'email' in kwargs:
            supplier_data['email'] = kwargs['email']
        if 'phone_number' in kwargs:
            supplier_data['phone_number'] = kwargs['phone_number']
        if 'items' in kwargs:
            supplier_data['items'] = kwargs['items']
        

        # Prepare the data to send in the PUT request
        json_data = {
            "company_name": company_name,
            "supplier": supplier_data
        }

        # You can adjust the URL to match the actual API endpoint
        response = requests.put(f'http://127.0.0.1:5000/suppliers/{supplier_id}', json=json_data)

        if response.status_code == 200:
            return {"message": "success", "data": None}, 200
        elif response.status_code == 404:
            return {"message": "error", "data": "Supplier not found"}, 404
        else:
            return {"message": "error", "data": None}, response.status_code
