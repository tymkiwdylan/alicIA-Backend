from typing import Dict
import requests
from .plugin import PluginInterface

class GetItemsPlugin(PluginInterface):

    def get_name(self) -> str:
        return "get_items"

    def get_description(self) -> str:
        return "Retrieve a list of items from a company's inventory via API."

    def get_parameters(self) -> Dict:
        """
        Return the parameters required for this plugin.
        In this case, there is a single parameter, 'company_name'.
        """
        parameters = {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "the name of the company"
                }
            }
        }
        
        return parameters

    def execute(self, **kwargs) -> Dict:
        company_name = kwargs['company_name']

        print(company_name)
        # You can adjust the URL to match the actual API endpoint
        json_data = {'company_name': company_name}
        response = requests.get('http://127.0.0.1:5000/items', json=json_data)

        if response.status_code == 200:
            return {"message": "success", "data": response.json().get('data')}, 200
        else:
            return {"message": "error", "data": None}, response.status_code
