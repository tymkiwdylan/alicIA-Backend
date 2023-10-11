from typing import Dict
import requests
from .plugin import PluginInterface

class AddSupplierPlugin(PluginInterface):

    def get_name(self) -> str:
        return "add_supplier"

    def get_description(self) -> str:
        return "Add a new supplier to a company's list of suppliers via API. Make sure you have all the parameters before executing"

    def get_parameters(self) -> Dict:
        """
        Return the parameters required for this plugin.
        In this case, there are two parameters: 'company_name' and 'supplier'.
        """
        parameters = {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "the name of the company"
                },
                "supplier": {
                    "type": "string",
                    "description": "the supplier name"
                },
                "email": {
                    "type": "string",
                    "description": "email of the supplier"
                },
                "phone_number": {
                    "type": "string",
                    "description": "Phhone number to contact the supplier"
                },
                 "items": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "id associated with the item"
                    },
                    "description": "list of the ids of items they supply"
                }
            }
        }
        
        return parameters

    def execute(self, **kwargs) -> Dict:
        company_name = kwargs['company_name']
        supplier = {
            'name': kwargs['supplier'],
            'email': kwargs['email'],
            'phone_number': kwargs['phone_number'],
            'items': kwargs['items']
        }

        # Prepare the data to send in the POST request
        json_data = {
            "company_name": company_name,
            "supplier": supplier
        }

        # You can adjust the URL to match the actual API endpoint
        response = requests.post('http://127.0.0.1:5000/suppliers', json=json_data)

        if response.status_code == 201:
            return {"message": "success", "data": None}, 201
        else:
            return {"message": "error", "data": None}, response.status_code
