from fastapi import APIRouter, HTTPException
import httpx
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import math
import json
import os
from pathlib import Path
from models import LocationRequest

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent
REGIONS_FILE = BASE_DIR / "shared" / "regions.json"
FALLBACK_FILE = BASE_DIR / "cache" / "fallback_data.json"

try:
    with open(REGIONS_FILE, "r") as f:
        REGIONS_DATA = json.load(f)
except FileNotFoundError:
    REGIONS_DATA = {} 

geolocator = Nominatim(user_agent="vanguard_earth_hydrology")

def calculate_wet_bulb(T: float, RH: float) -> float:
    tw = (T * math.atan(0.151977 * math.sqrt(RH + 8.313659)) + 
          math.atan(T + RH) - math.atan(RH - 1.676331) + 
          0.00391838 * math.pow(RH, 1.5) * math.atan(0.023101 * RH) - 4.686035)
    
    return max(15.0, tw)

def get_state_from_coords(lat: float, lon: float) -> str:
    try:
        location = geolocator.reverse(f"{lat}, {lon}", timeout=3)
        if location and "address" in location.raw:
            state = location.raw["address"].get("state", "")
            if state in REGIONS_DATA:
                return state
            for known_state in REGIONS_DATA.keys():
                if known_state in state or state in known_state:
                    return known_state
    except (GeocoderTimedOut, GeocoderServiceError, Exception):
        pass
    return "default"

@router.post("/analyze-location")
async def analyze_location(request: LocationRequest):
    try:
        state_name = get_state_from_coords(request.latitude, request.longitude)
        depletion_rate = REGIONS_DATA[state_name]["aquifer_depletion_rate_meters_yr"]

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={request.latitude}&longitude={request.longitude}&current=temperature_2m,relative_humidity_2m"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(weather_url, timeout=5.0)
            response.raise_for_status()
            weather_data = response.json()
            
        temp = weather_data["current"]["temperature_2m"]
        humidity = weather_data["current"]["relative_humidity_2m"]

        wet_bulb = calculate_wet_bulb(temp, humidity)
        
        raw_stress = ((wet_bulb - 25) * 5) + (depletion_rate * 8)
        water_stress = max(0, min(100, int(raw_stress)))
        
        habitability = 100 - water_stress
        crop_loss = int(water_stress * 0.4)
        migration_pressure = int(water_stress * 0.8)
        
        years_remaining = 3 + math.pow((habitability / 12), 2)
        collapse_yr = 2025 + int(years_remaining)
        

        if habitability < 30:
            status = "CRITICAL"
        elif habitability < 60:
            status = "WARNING"
        else:
            status = "SAFE"

        if status == "CRITICAL":
            blueprints = ["Deep Recharges", "Canopy Cooling", "Solar Microgrids"]
            surge = 14.5
        elif status == "WARNING":
            blueprints = ["Watershed Restoration", "Drip Irrigation"]
            surge = 8.2
        else:
            blueprints = ["Rainwater Harvesting", "Crop Rotation"]
            surge = 2.1

        return {
            "status": status,
            "habitability_score": habitability,
            "metrics": {
                "current_wet_bulb_celsius": round(wet_bulb, 1),
                "aquifer_depletion_rate_meters_yr": float(depletion_rate)
            },
            "domino_effect": {
                "crop_yield_loss_percent": crop_loss,
                "migration_pressure_score": migration_pressure,
                "water_stress_index": water_stress
            },
            "timeline": {
                "collapse_year": collapse_yr
            },
            "prevention_blueprints": blueprints,
            "migration_pipeline": {
                "safe_zone_target": "Elevated Inland Corridor",
                "distance_km": 420,
                "destination_utility_surge_percent": surge
            }
        }

    except (httpx.RequestError, httpx.HTTPStatusError, KeyError) as e:
        print(f"Live API Failed: {e}. Loading fallback data.")
        try:
            with open(FALLBACK_FILE, "r") as f:
                return json.load(f)
        except Exception as fallback_error:
            raise HTTPException(status_code=500, detail="Live API and Fallback both failed.")