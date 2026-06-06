from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("GROK_API_KEY"), base_url="https://api.x.ai/v1")

try:
    print("Models: ")
    models = client.models.list()
    for model in models:
        print(f"Available ID: {model.id}")
except Exception as e:
    print(f"Error: {e}")