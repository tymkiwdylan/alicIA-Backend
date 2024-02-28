import requests

class Search():
    settings = {
                "name": "Search",
                "description": "Search for an item in the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query that is used to search for an item"
                    },
                    "company_name": {
                        "type": "string",
                        "description": "name of the company the assistant works for"
                    }
                    },
                    "required": [
                    "query"
                    ]
                }
            }
    @staticmethod
    def execute(**kwargs):
        # The URL for the API endpoint (you will replace this with the actual URL)
        url = "http://chain-layer:7000/search"
        query = kwargs.get('query')

        try:
            # Making a GET request to the API
            response = requests.get(url, params={'query': query})

            # Check if the response is successful
            if response.status_code == 200:
                # You might need to process the response data as needed
                return {
                    "message": "Successfully retrieved item/s",
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
