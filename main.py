from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api_database import router as db_router
from api_hydrology import router as hydrology_router
from api_ai import router as ai_router
from api_report import router as report_router
app = FastAPI(title="Vanguard Earth API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(report_router, prefix="/api")
app.include_router(db_router, prefix="/api")
app.include_router(hydrology_router, prefix="/api")
app.include_router(ai_router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "running"}


