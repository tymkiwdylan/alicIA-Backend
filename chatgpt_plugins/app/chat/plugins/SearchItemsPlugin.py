from typing import Dict
import requests
from .plugin import PluginInterface

class ItemSearchPlugin(PluginInterface):

    def get_name(self) -> str:
        return "item_search"

    def get_description(self) -> str:
        return "Search for items in the company's inventory via API."

    def get_parameters(self) -> Dict:
        """
        Return the parameters required for this plugin.
        In this case, there are two parameters: 'company_name' and 'query'.
        """
        parameters = {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "the name of the company"
                },
                "query": {
                    "type": "string",
                    "description": "the pymongo query for searching items. You may use REGEX expressions"
                }
            },
            "required": ['company_name', 'query']
        }
        
        return parameters

    def execute(self, **kwargs) -> Dict:
        company_name = kwargs['company_name']
        query = kwargs['query']
        
        print(query)

        # Prepare the data to send in the POST request
        json_data = {
            "company_name": company_name,
            "query": query
        }

        # You can adjust the URL to match the actual API endpoint
        response = requests.post('http://127.0.0.1:5000/items/search', json=json_data)

        if response.status_code == 200:
            return {"message": "success", "data": response.json().get('data')}, 200
        else:
            return {"message": "error", "data": None}, response.status_code
