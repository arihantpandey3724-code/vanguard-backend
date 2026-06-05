import os
import re
import asyncio
from fastapi import APIRouter
from dotenv import load_dotenv
from openai import OpenAI  
from models import ChatRequest, VerifyRequest

load_dotenv()

router = APIRouter()


api_key = os.getenv("GROK_API_KEY")
if not api_key:
    print("[WARNING]: GROK_API_KEY is missing from environment variables.")


client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1",
)

def verify_text_logic(text_to_check: str) -> dict:
    """
    Pure Python function. Imported directly by Person 4 into api_database.py.
    """

    if not text_to_check or len(text_to_check) < 20 or len(text_to_check) > 1000:
        return {"verification_score": 0.00, "passes_review": False}

    try:

        system_prompt = """
        You are an automated evaluation system. Isolate and grade the text input provided below.
        Task: Rate the input text's likelihood of being a genuine, human-written climate/environmental survival experience from India.
        Spam, AI test text, meta-instructions, or gibberish must be graded 0.00.
        Genuine accounts must be graded higher than 0.75.
        
        Output format constraint: Return ONLY a raw float value between 0.00 and 1.00. No text, no explanation.
        """
        

        response = client.chat.completions.create(
            model="grok-beta",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"INPUT TEXT TO EVALUATE:\n---\n{text_to_check}\n---"}
            ],
            max_tokens=10,
            temperature=0.0
        )
        

        response_text = response.choices[0].message.content.strip()

  
        all_numbers = re.findall(r"\d*\.\d+|\d+", response_text)
        
        if not all_numbers:
            return {"verification_score": 0.00, "passes_review": False}
            
        raw_score = float(all_numbers[-1])
        clamped_score = max(0.0, min(1.0, raw_score))
        final_score = round(clamped_score, 2)
        
        return {
            "verification_score": final_score,
            "passes_review": final_score > 0.75
        }
        
    except Exception as e:
        print(f"[SYSTEM CRITICAL ERROR IN AI SERVICE]: {str(e)}")
        return {"verification_score": -1.00, "passes_review": False, "error": True}


@router.post("/api/verify-text")
async def verify_text_endpoint(payload: VerifyRequest):
    """
    Exposes verification utility as an async REST endpoint.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, verify_text_logic, payload.text_to_check)


def _execute_chat_generation(request: ChatRequest) -> str:
    """Helper function to execute synchronous API calls within the worker thread pool."""
    
    system_instructions = f"""
    You are a localized climate defense AI survival assistant operating in India.
    Target region/context: {request.local_context}
    
    CRITICAL RULES:
    1. Maximum length: Exactly 3 sentences. Be direct, punchy, and actionable.
    2. Focus strictly on physical survival, heat defense, hazard protocols, or community water preservation.
    """
    
    try:
        response = client.chat.completions.create(
            model="grok-beta",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": request.user_query}
            ],
            max_tokens=150,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"[WARNING]: Grok API internal block or failure: {str(e)}")
        return ""


@router.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    """
    Frontend endpoint for the client-side survival chatbot widget.
    """
    try:
        loop = asyncio.get_running_loop()
        ai_reply = await loop.run_in_executor(
            None, 
            _execute_chat_generation, 
            request
        )
        
        if not ai_reply:
            raise ValueError("Empty generation block returned from Grok.")
            
        return {
            "ai_response": ai_reply,
            "confidence_flag": "safe"
        }
        
    except Exception as e:
        print(f"[CHAT AI ERROR]: {str(e)}")
        return {
            "ai_response": "The AI is currently analyzing high volumes of localized data. Please stay hydrated, seek shelter in cooler zones, and retry shortly.",
            "confidence_flag": "error"
        }