import os
import requests

# Load password from environment variable
password = os.getenv('API_PASSWORD') #export API_PASSWORD=<password>"

if not password:
    raise ValueError("Password is not set in the environment variables")

# Define the URL and headers
url = "https://api.enderphan.info/completion"
headers = {"Content-Type": "application/json"}

prompt = "Building a website can be done in 10 simple steps:"
# Define the authentication and payload
auth = ('admin', password)
data = {
    "prompt": prompt,
    "n_predict": 2048
}

# Make the POST request
response = requests.post(url, headers=headers, auth=auth, json=data)

# Check if the response is successful
if response.status_code == 200:
    response_json = response.json()
    content_value = response_json.get("content", "")
    print("Content:", content_value)
else:
    print(f"Error: Received status code {response.status_code}")