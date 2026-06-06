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
        "trend_analysis": {
            "summary": f"Could not verify specific data for '{location}'. The location may be invalid or servers are currently overloaded.", 
            "prediction": "Converging threats of severe water table depletion and rising thermal stress will soon render baseline conditions in this region too drastic for human survival, directly forcing widespread and inevitable climate migration.", 
            "status": "UNKNOWN"
        },
        "individual_actions": [
            "Retrofit living spaces with phase-change materials (PCMs) to absorb daytime thermal spikes.",
            "Deploy localized atmospheric water generators (AWGs) to extract moisture directly from ambient air.",
            "Utilize sub-surface greywater irrigation to eliminate evaporation loss.",
            "Construct DIY passive downdraft evaporative cooling towers (windcatchers) to lower indoor temperatures."
        ],
        "authority_actions": [
            "Engineer decentralized, subterranean thermal refuges for multi-week grid collapse scenarios.",
            "Enforce strict 'managed retreat' zoning laws in high-risk perimeter zones.",
            "Deploy autonomous deep-bed aquifer injection wells to force-feed monsoonal runoff back into the water table.",
            "Construct regional greywater-to-potable closed-loop filtration plants."
        ]
    }

@router.post("/generate-report")
async def generate_report(request: ReportRequest):
    try:
        prompt = f"""
        You are an advanced environmental and survival engineer for VanGuard Earth. 
        Analyze the location: "{request.location}".

        CRITICAL INSTRUCTIONS:
        1. LOCATION VALIDATION: Silently recognize and correct any minor typos. If the location is fake, set 'status' to "UNKNOWN" and state it cannot be verified.
        2. BIOME & TERRAIN IDENTIFICATION: Internally identify the specific geographic biome of this location (e.g., is it a Coastal Megacity, an Arid Desert, a Himalayan Foothill, or an Inland River Plain?). YOUR ACTIONS MUST EXPLICITLY MATCH THIS BIOME.
        3. DEEP FACTUAL SUMMARY: Provide a dense, 4-5 sentence analysis of real climate facts for this specific region. 
        4. MULTI-CAUSAL MIGRATION PREDICTION: Explicitly state that converging issues (e.g., agricultural failure, lethal wet-bulb temperatures, dry aquifers) will make the region physically and economically unlivable, forcing inevitable widespread migration.
        
        5. HYPER-SPECIFIC INDIVIDUAL ACTIONS (STRICT BLACKLIST ACTIVE):
           - YOU ARE STRICTLY FORBIDDEN from suggesting: "rainwater harvesting", "planting trees", "carpooling", "saving water", "solar panels", or "awareness".
           - Provide exactly 4 to 6 advanced survival tactics. 
           - CRITICAL: These must be 100% unique to the biome. (e.g., If coastal: focus on saltwater intrusion, storm surges, and marine food webs. If inland plains: focus on extreme dry heat, aquifer tapping, and crop desiccation). DO NOT output the same tactics for coastal and inland cities.

        6. HYPER-SPECIFIC AUTHORITY ACTIONS (STRICT BLACKLIST ACTIVE):
           - YOU ARE STRICTLY FORBIDDEN from suggesting: "public awareness campaigns", "planting trees", "building seawalls", or "reducing emissions".
           - Provide exactly 4 to 6 hardcore, structural geo-engineering actions tailored strictly to the terrain identified in Step 2.

        Return ONLY a JSON object with this exact structure:
        {{
            "trend_analysis": {{
                "summary": "Detailed, factual climate data analysis. Do NOT start with 'The correct name is...'",
                "prediction": "A stark forecast explicitly stating that converging causes will force inevitable widespread migration.",
                "status": "CRITICAL" | "WARNING" | "STABLE" | "UNKNOWN"
            }},
            "individual_actions": [
                "Advanced, geography-specific survival tactic without using banned words...",
                "Advanced, geography-specific survival tactic without using banned words...",
                "..."
            ],
            "authority_actions": [
                "Advanced, formal structural geo-engineering action specific to this terrain...",
                "Advanced, formal structural geo-engineering action specific to this terrain...",
                "..."
            ]
        }}
        """
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a strict JSON-outputting climate API. Never output markdown outside the JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" },
            temperature=0.7 
        )
        
        raw_content = response.choices[0].message.content
        return json.loads(raw_content)

    except json.JSONDecodeError:
        print("Backend Error: AI returned malformed JSON.")
        return get_fallback_data(request.location)
    except Exception as e:
        print(f"Backend Error: {e}")
        return get_fallback_data(request.location)