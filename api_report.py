from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
import os
import json

router = APIRouter()
client = OpenAI(api_key=os.getenv("GROK_API_KEY"), base_url="https://api.x.ai/v1")

class ReportRequest(BaseModel):
    location: str

@router.post("/generate-report")
async def generate_report(request: ReportRequest):
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
        model="grok-2",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)