import requests

url = 'http://127.0.0.1:8000/my-data/'
data = {'key1': 'value1', 'key2': 'value2'}

response = requests.post(url, json=data)
print(response.status_code)
print(response.json())