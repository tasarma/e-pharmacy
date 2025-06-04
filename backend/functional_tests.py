import requests

response = requests.get("http://localhost:8000")
assert "Congratulations!" in response.text
print("OK")
