import requests
import json

class CarpetClient:
    def __init__(self, url, api_key, *args, **kwargs):
        self.url = url
        self.api_key = api_key
        
    def load_generations(self, file_path, dataset_name):
        params = {
            'datasetName': dataset_name,
            'apiKey': self.api_key
        }
        with open(file_path, 'r') as f:
            data = json.load(f)
        response = requests.post(self.url + "/api/eval", params=params, json=data, headers={'Content-Type': 'application/json'})
        return response