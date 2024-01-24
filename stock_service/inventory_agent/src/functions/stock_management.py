import requests

class StockManagement():
    settings = {
        "name": "StockManagement",
        "description": "Manage stock items (Add, Update, Delete)",
        "parameters": {
            "type": "object",
            "properties": {
                "queries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "option": {
                                "type": "string",
                                "enum": ["add", "update", "delete"]
                            },
                            "item": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string"
                                    },
                                    "SKU": {
                                        "type": "string"
                                    },
                                    "description": {
                                        "type": "string"
                                    },
                                    "cost": {
                                        "type": "integer",
                                        "minimum": 0
                                    },
                                    "price": {
                                        "type": "integer",
                                        "minimum": 0
                                    }
                                },
                                "required": ["name", "SKU", "description", "cost", "price"]
                            },
                            "new_level": {
                                "type": "integer"
                            },
                            "id": {
                                "type": "string"
                            }
                        },
                        "required": ["option"]
                    }
                },
            },
            "required": ["queries", ]
        }
    }

    @staticmethod
    def execute(company_name, queries):
        # The URL for the API endpoint
        url = "http://chain-layer:7000/stock"

        try:
            # Making a POST request to the API with the queries
            response = requests.post(url, json={"queries": queries, 'company_name': company_name})

            # Check if the response is successful
            if response.status_code == 200:
                return {
                    "message": "Stock successfully managed",
                    "data": response.json()  # Process the response data as needed
                }
            elif response.status_code == 400:
                return {
                    "message": "Invalid request",
                    "data": None,
                    "status_code": 400
                }
            elif response.status_code == 500:
                return {
                    "message": "Server error",
                    "data": None,
                    "status_code": 500
                }
            else:
                return {
                    "message": "Unexpected error",
                    "data": None,
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "message": str(e),
                "data": None
            }
