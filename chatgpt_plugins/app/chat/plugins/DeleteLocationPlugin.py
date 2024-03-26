from typing import Dict
import requests
from .plugin import PluginInterface

class DeleteLocationPlugin(PluginInterface):

    def get_name(self) -> str:
        return "delete_location"

    def get_description(self) -> str:
        return "Delete a specific location by its ID via API. ASK FOR CONFIRMATION"

    def get_parameters(self) -> Dict:
        """
        Return the parameters required for this plugin.
        In this case, there are two parameters: 'company_name' and 'location_id'.
        """
        parameters = {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "the name of the company"
                },
                "location_id": {
                    "type": "string",
                    "description": "ID of the location to delete"
                }
            },
            "required": ["company_name", "location_id"]
        }
        
        return parameters

    def execute(self, **kwargs) -> Dict:
        company_name = kwargs['company_name']
        location_id = kwargs['location_id']

        # Prepare the data to send in the DELETE request
        json_data = {
            "company_name": company_name
        }

        # You can adjust the URL to match the actual API endpoint
        response = requests.delete(f'http://127.0.0.1:5000/locations/{location_id}', json=json_data)

        if response.status_code == 200:
            return {"message": "success", "data": None}, 200
        elif response.status_code == 404:
            return {"message": "error", "data": "Location not found"}, 404
        else:
            return {"message": "error", "data": None}, response.status_code
