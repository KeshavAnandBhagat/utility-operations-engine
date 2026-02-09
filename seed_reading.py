from models import SessionLocal, SmartMeterReading
from datetime import datetime

db = SessionLocal()

# Simulate a reading arriving "Just now"
reading = SmartMeterReading(
    meter_no="SCHNEIDERE123",
    reading_timestamp=datetime.now(),
    kwh_cumulative=6856.93,
    kvah_cumulative=6900.00,
    tod_zone1=500.0,
    tod_zone2=600.0,
    tod_zone3=109.0, # The 109 units for TOD
    event_code="NORMAL"
)

db.add(reading)
db.commit()
print("✅ Smart Meter Reading Injected into MDM Database")
db.close()