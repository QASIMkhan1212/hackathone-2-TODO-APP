import requests

api_key = "your_groq_api_key_here"

response = requests.get(
    "https://api.groq.com/openai/v1/models",
    headers={"Authorization": f"Bearer {api_key}"}
)

if response.status_code == 200:
    models = response.json().get("data", [])
    print("Available Groq models:")
    for model in models:
        print(f"  - {model['id']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
