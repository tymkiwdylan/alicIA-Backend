import requests

class StockMovementLogger():
    settings = {
        "name": "StockMovementLogger",
        "description": "Log a stock movement",
        "parameters": {
            "type": "object",
            "properties": {
                "movement": {
                    "type": "object",
                    "properties": {
                        "item_id": {
                            "type": "string"
                        },
                        "quantity": {
                            "type": "integer"
                        },
                        "movement_type": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        }
                    }
                }
            },
            "required": ["movement"]
        }
    }

    @staticmethod
    def execute(movement):
        # The URL for the API endpoint
        url = "http://chain-layer:7000/movement-log"

        try:
            # Making a POST request to the API with the movement data
            response = requests.post(url, json={"movement": movement})

            # Check if the response is successful
            if response.status_code == 200:
                return {
                    "message": "Stock movement logged successfully",
                    "data": response.json()  # Process the response data as needed
                }
            else:
                return {
                    "message": "Failed to log stock movement",
                    "data": None,
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "message": str(e),
                "data": None
            }
