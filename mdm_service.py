# FILE: mdm_service.py
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from models import SessionLocal, SmartMeterReading
from datetime import datetime

app = FastAPI(title="MDM Simulator Service")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"status": "MDM System Online", "version": "1.0.0"}

@app.get("/readings/{meter_no}")
def get_meter_reading(meter_no: str, bill_date: str = None):
    """
    Simulates fetching the 'Golden Record' for billing.
    Usage: GET /readings/SCHNEIDEREZ0410851?bill_date=2025-08-01
    """
    db = SessionLocal()
    
    # Default to today if no date provided
    target_date = datetime.now()
    if bill_date:
        try:
            target_date = datetime.strptime(bill_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # LOGIC: Find the latest reading ON or BEFORE the bill date
    reading = db.query(SmartMeterReading)\
        .filter(SmartMeterReading.meter_no == meter_no)\
        .filter(SmartMeterReading.reading_timestamp <= target_date)\
        .order_by(SmartMeterReading.reading_timestamp.desc())\
        .first()

    db.close()

    if not reading:
        raise HTTPException(status_code=404, detail="No reading found for this meter/date")

    # Return clean JSON to the caller
    return {
        "meter_no": reading.meter_no,
        "timestamp": reading.reading_timestamp.isoformat(),
        "kwh": reading.kwh_cumulative,
        "kvah": reading.kvah_cumulative,
        "tod": {
            "zone1": reading.tod_zone1,
            "zone2": reading.tod_zone2,
            "zone3": reading.tod_zone3
        }
    }

# To run this: uvicorn mdm_service:app --reload