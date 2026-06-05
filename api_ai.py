import os
import re
import google.generativeai as genai
from fastapi import APIRouter
from models import ChatRequest, VerifyRequest


router = APIRouter()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')


def verify_text_logic(text_to_check: str) -> dict:
    """
    Pure Python function. Person 4 will import this directly into
    api_database.py to avoid an internal network HTTP deadlock.
    """

    if not text_to_check or len(text_to_check) < 20:
        return {"verification_score": 0.00, "passes_review": False}

    try:

        verification_prompt = f"""
        You are an advanced text authentication system for a climate platform.
        Analyze the following text and determine if it is a genuine, human-written 
        survival hack or climate adaptation experience from India, or if it is AI-generated spam/gibberish.
        
        Provide your assessment as a confidence score between 0.00 and 1.00.
        A score of 1.00 means completely genuine human text. A score of 0.00 means pure spam.
        
        Respond ONLY with the numerical score (e.g., 0.85). Do not include any other text.
        
        Text to check: "{text_to_check}"
        """
        

        response = model.generate_content(verification_prompt)
        response_text = response.text.strip() if response.text else "0.50"
        

        match = re.search(r"[-+]?\d*\.\d+|\d+", response_text)
        raw_score = float(match.group()) if match else 0.50
        

        clamped_score = max(0.0, min(1.0, raw_score))
        

        final_score = round(clamped_score, 2)
        
        return {
            "verification_score": final_score,
            "passes_review": final_score > 0.75
        }
        
    except Exception as e:

        return {"verification_score": 0.50, "passes_review": False}



@router.post("/api/verify-text")
def verify_text_endpoint(payload: VerifyRequest):
    """
    Exposes the verification utility as a REST endpoint if needed for testing.
    """
    return verify_text_logic(payload.text_to_check)

@router.post("/api/chat")
def chat_with_ai(request: ChatRequest):
    """
    Frontend endpoint for the survival chatbot widget.
    Processes language toggles and group vulnerability filters.
    """
    try:
        system_instructions = f"""
        You are a highly localized climate defense AI survival assistant operating in India.
        Your current target audience is in this climate region: {request.local_context}.
        The user belongs to this highly vulnerable demographic group: {request.vulnerable_group}.
        
        CRITICAL RULES:
        1. You MUST respond entirely in this language: {request.language}. No mixed phrasing.
        2. Keep your response to a MAXIMUM of 3 sentences. Be punchy, practical, and direct.
        3. Falsely optimistic text is banned; focus strictly on emergency safety, water defense, and climate survival strategies.
        4. Refuse to answer queries unrelated to environmental survival.
        """
        
        full_prompt = f"{system_instructions}\n\nUser Query: {request.user_query}"
        
        response = model.generate_content(full_prompt)
        ai_reply = response.text.strip() if response.text else ""
        
        if not ai_reply:
            raise ValueError("Empty response received from LLM cluster.")
            
        return {
            "ai_response": ai_reply,
            "confidence_flag": "safe"
        }
        
    except Exception as e:
        fallback_messages = {
            "hindi": "एआई वर्तमान में भारी डेटा का विश्लेषण कर रहा है। कृपया हाइड्रेटेड रहें, सुरक्षित स्थान पर शरण लें और थोड़ी देर बाद पुनः प्रयास करें।",
            "english": "The AI is currently analyzing high volumes of localized data. Please stay hydrated, seek shelter in cooler zones, and retry shortly."
        }
        
        chosen_language = request.language.lower() if request.language else "english"
        return {
            "ai_response": fallback_messages.get(chosen_language, fallback_messages["english"]),
            "confidence_flag": "error"
        }