import requests

url = 'http://127.0.0.1:5000/predict'
data = {"features": [7.2, 0.5, 120, 0.02]}  # Example input
response = requests.post(url, json=data)
print(response.json())