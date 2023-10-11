from typing import Dict
import requests
from .plugin import PluginInterface

class GetSuppliersPlugin(PluginInterface):

    def get_name(self) -> str:
        return "get_suppliers"

    def get_description(self) -> str:
        return "Get a list of suppliers for a specific company via API."

    def get_parameters(self) -> Dict:
        """
        Return the parameters required for this plugin.
        In this case, there is a single parameter: 'company_name'.
        """
        parameters = {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "the name of the company"
                }
            },
            "required": ["company_name"]
        }
        
        return parameters

    def execute(self, **kwargs) -> Dict:
        company_name = kwargs['company_name']

        # Prepare the data to send in the GET request
        json_data = {
            "company_name": company_name
        }

        # You can adjust the URL to match the actual API endpoint
        response = requests.get('http://127.0.0.1:5000/suppliers', json=json_data)

        if response.status_code == 200:
            return {"message": "success", "data": response.json().get('data')}, 200
        else:
            return {"message": "error", "data": None}, response.status_code
