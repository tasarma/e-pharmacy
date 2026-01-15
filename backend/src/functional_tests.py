import requests

response = requests.get("http://localhost:8000/health/")
assert response.status_code == 200
print("OK")
