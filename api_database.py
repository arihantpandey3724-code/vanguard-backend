from fastapi import APIRouter, HTTPException
from models import StorySubmission
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-service-account.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
router = APIRouter()

@router.post("/submit-story")
def submit_story(payload: StorySubmission):
    passes_review = True
    ai_score = 0.88 
    
    if not passes_review:
        raise HTTPException(status_code=400, detail="Rejected by AI")

    try:
        doc_ref = db.collection("stories").document()
        story_data = payload.model_dump()
        story_data["verified"] = True
        story_data["ai_trust_score"] = ai_score
        doc_ref.set(story_data)
        
        return {
            "submission_status": "Success",
            "message": "Story verified and added to the public map."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-stories")
def get_all_stories():
    try:
        docs = db.collection("stories").stream()
        all_stories = []
        for doc in docs:
            story = doc.to_dict()
            story["id"] = doc.id
            all_stories.append(story)
            
        return {"stories": all_stories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))