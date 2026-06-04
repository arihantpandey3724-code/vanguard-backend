from fastapi import FastAPI
from api_database import router as db_router

app = FastAPI(title="Vanguard Earth API")
app.include_router(db_router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "running"}