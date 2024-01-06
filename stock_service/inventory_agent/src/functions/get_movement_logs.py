import requests

class GetMovementLog():
    settings = {
        "name": "GetMovementLog",
        "description": "Retrieve stock movement logs",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }

    @staticmethod
    def execute(**kwargs):
        # The URL for the API endpoint
        url = "http://chain-layer:7000/movement-log"

        try:
            # Making a GET request to the API
            response = requests.get(url, params=kwargs)

            # Check if the response is successful
            if response.status_code == 200:
                # Assuming the response is JSON and contains the required data
                return {
                    "message": "Successfully retrieved stock movement logs",
                    "data": response.json()  # Process the response data as needed
                }
            else:
                return {
                    "message": "Failed to retrieve stock movement logs",
                    "data": None,
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "message": str(e),
                "data": None
            }
