from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# 1. Create the router
router = APIRouter()

# --- THE FIX: Changed back to GROK (with a K) to match your working .env file! ---
client = OpenAI(
    api_key=os.getenv("GROK_API_KEY"), 
    base_url="https://api.groq.com/openai/v1"
)

# 3. Define the incoming request format
class ChatRequest(BaseModel):
    message: str

# 4. Create the Chatbot Endpoint
@router.post("/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        # Use the exact same client pattern as your report generator
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are Vanguard AI, a tactical advisor for climate survival. Keep answers short, punchy, and focused on extreme heat, water scarcity, and survival strategies. Limit responses to 3 sentences max."
                },
                {
                    "role": "user",
                    "content": request.message,
                }
            ]
        )
        
        reply = response.choices[0].message.content
        return {"response": reply}
        
    except Exception as e:
        print(f"Chat API Error: {e}")
        return {"response": "Vanguard AI is currently recalibrating. Please try again."}