import google.generativeai as genai

genai.configure(api_key="AIzaSyAZ8JR4sjv9c_2WvYLudxzl1ICz95XWKoA")

print("Available models:")
try:
    client = genai._client.get_default_generative_client()
    for model in client.list_models():
        print(f"  - {model.name}")
except Exception as e:
    print(f"Method 1 failed: {e}")
    print("\nTrying alternative method...")

    # Try direct API call
    import requests
    url = "https://generativelanguage.googleapis.com/v1beta/models?key=AIzaSyAZ8JR4sjv9c_2WvYLudxzl1ICz95XWKoA"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for model in data.get("models", []):
            methods = model.get("supportedGenerationMethods", [])
            if "generateContent" in methods:
                print(f"  - {model['name']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
