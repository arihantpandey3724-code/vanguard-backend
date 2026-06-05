from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
import json

router = APIRouter()
client = OpenAI(api_key=os.getenv("GROK_API_KEY"), base_url="https://api.groq.com/openai/v1")

class ReportRequest(BaseModel):
    location: str

def get_fallback_data(location):
    return {
        "trend_analysis": {"summary": f"Data for {location} indicates increased variability.", "prediction": "Continued climate volatility expected.", "status": "WARNING"},
        "individual_actions": ["Monitor local water levels", "Adopt water-efficient practices"],
        "authority_actions": ["Evaluate regional infrastructure", "Improve drainage networks"]
    }

@router.post("/generate-report")
async def generate_report(request: ReportRequest):
    try:
        prompt = f"""
        Analyze climate trends for {request.location} over the last 20 years.
        Predict future climate migration risks and provide actionable strategies.
        Return ONLY a JSON object with this exact structure:
        {{
            "trend_analysis": {{"summary": "...", "prediction": "...", "status": "CRITICAL/STABLE"}},
            "individual_actions": ["...", "..."],
            "authority_actions": ["...", "..."]
        }}
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Groq model
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        
        raw_content = response.choices[0].message.content
        return json.loads(raw_content)

    except json.JSONDecodeError:
        print("Backend Error: AI returned malformed JSON.")
        return get_fallback_data(request.location)
    except Exception as e:
        print(f"Backend Error: {e}")
        return get_fallback_data(request.location)