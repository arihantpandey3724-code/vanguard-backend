from openai import OpenAI
import os

# This uses your existing GROK_API_KEY from your environment
client = OpenAI(api_key=os.getenv("GROK_API_KEY"), base_url="https://api.x.ai/v1")

try:
    print("Checking available models...")
    models = client.models.list()
    for model in models:
        print(f"Available ID: {model.id}")
except Exception as e:
    print(f"Error: {e}")