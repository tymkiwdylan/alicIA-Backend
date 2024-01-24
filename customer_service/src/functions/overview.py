import requests

class Overview():
    settings = {
            "name": "Overview",
            "description": "Give an overview of the inventory",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "name of the company the assistant works for"
                    }
                    },
                "required": ["company_name"]
            }
        }
    @staticmethod
    def execute(**kwargs):
        # The URL for the API endpoint
        url = "http://chain-layer:7000/overview"

        try:
            # Making a GET request to the API
            response = requests.get(url)

            # Check if the response is successful
            if response.status_code == 200:
                # You might need to process the response data as needed
                return {
                    "message": "Successfully retrieved inventory summary",
                    "data": response.json()['data']  # Assuming the response is JSON
                }
            else:
                return {
                    "message": "Failed to retrieve data",
                    "data": None,
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "message": str(e),
                "data": None
            }
