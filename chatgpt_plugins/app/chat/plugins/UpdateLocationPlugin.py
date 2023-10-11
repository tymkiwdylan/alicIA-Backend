from typing import Dict
import requests
from .plugin import PluginInterface

class UpdateLocationPlugin(PluginInterface):

    def get_name(self) -> str:
        return "update_location"

    def get_description(self) -> str:
        return "updates a existing location of a company via API."

    def get_parameters(self) -> Dict:
        """
        Return the parameters required for this plugin.
        In this case, there are two parameters: 'company_name' and 'location'.
        """
        parameters = {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "the name of the company"
                },
                "location_id":{
                    "type": "string",
                    "description": "the id of the location"
                },                   
                "name": {
                    "type": "string",
                    "description": "Name or identifier of the location"
                },
                "description": {
                    "type": "string",
                    "description": "Description or additional details about the location"
                },
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {
                            "type": "string",
                            "description": "Street address"
                        },
                        "city": {
                            "type": "string",
                            "description": "City"
                        },
                        "state": {
                            "type": "string",
                            "description": "State or province"
                        },
                        "postal_code": {
                            "type": "string",
                            "description": "Postal code or ZIP code"
                        },
                        "country": {
                            "type": "string",
                            "description": "Country"
                        }
                    },
                    "required": ["street", "city", "state", "postal_code", "country"],
                    "description": "Address information"
                },
                "capacity": {
                    "type": "number",
                    "description": "Maximum storage capacity of the location"
                },
                "current_stock": {
                    "type": "number",
                    "description": "Current stock level at the location"
                },
                "available_capacity": {
                    "type": "number",
                    "description": "Available storage capacity"
                },
                "status": {
                    "type": "string",
                    "enum": ["Active", "Inactive", "Under Maintenance"],
                    "description": "Status of the location"
                }
            },
            "required": ["company_name", "location_id"],
        }
        
        return parameters

    def execute(self, **kwargs) -> Dict:
        company_name = kwargs['company_name']
        location_id = kwargs['location_id']
        
        location_data = {}
        if 'name' in kwargs:
            location_data['name'] = kwargs['name']
        if 'description' in kwargs:
            location_data['description'] = kwargs['description']
        if 'address' in kwargs:
            location_data['address'] = kwargs['address']
        if 'capacity' in kwargs:
            location_data['capacity'] = kwargs['capacity']
        if 'current_stock' in kwargs:
            location_data['current_stock'] = kwargs['current_stock']
        if 'available_capacity' in kwargs:
            location_data['available_capacity'] = kwargs['available_capacity']
        if 'status' in kwargs:
            location_data['status'] = kwargs['status']
        
        # Prepare the data to send in the POST request
        json_data = {
            "company_name": company_name,
            "location": location_data
        }

        # You can adjust the URL to match the actual API endpoint
        response = requests.post('http://127.0.0.1:5000/locations', json=json_data)

        if response.status_code == 201:
            return {"message": "success", "data": None}, 201
        else:
            return {"message": "error", "data": None}, response.status_code
