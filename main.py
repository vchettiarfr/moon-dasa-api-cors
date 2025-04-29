
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

print("✅ FastAPI with CORS is running!")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/moon_nakshatra_dasa")
def moon_dasa(date: str = Query(...), latitude: float = Query(...), longitude: float = Query(...)):
    return {
        "nakshatra": "Rohini",
        "moon_longitude": 53.2,
        "pada": 4,
        "dasa": "Moon",
        "bukti": "Rohini",
        "antra": "Mercury",
        "sukshma": "Ketu",
        "start_time": datetime.fromisoformat(date).strftime("%d/%m/%Y %H:%M:%S")
    }
