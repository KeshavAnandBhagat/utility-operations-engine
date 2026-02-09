import time
import random
from faker import Faker
from sqlalchemy.orm import Session
from models import engine, Consumer, SmartMeterReading, Base
from datetime import date, datetime

# Setup
fake = Faker('en_IN') # Indian Names/Addresses
session = Session(bind=engine)

NUM_USERS = 10000

def generate_bulk_data():
    print(f"--- 🚀 STARTING BULK SEED FOR {NUM_USERS} USERS ---")
    start_time = time.time()

    consumers = []
    readings = []
    
    # 1. Generate Data in Memory (Fast)
    for i in range(NUM_USERS):
        # Create unique IDs
        cid = f"N{1000000000 + i}"
        meter = f"METER{500000 + i}"
        
        # Random Load/Zone
        zone = random.choice(["Balaghat(T)", "Indore(C)", "Jabalpur(N)"])
        load = random.choice([1.0, 2.0, 3.0, 5.0])
        
        # Consumer Object
        c = {
            "id": cid,
            "old_service_no": f"OLD-{i}",
            "name": fake.name(),
            "address": fake.address().replace("\n", ", "),
            "mobile": fake.phone_number(),
            "email": fake.email(),
            "zone": zone,
            "division": "MP_EAST",
            "dc_code": "DC1",
            "feeder_code": str(random.randint(1000, 9999)),
            "dtr_code": str(random.randint(100, 999)),
            "connection_type": "Domestic",
            "purpose": "Residential",
            "phase": "SINGLE",
            "load_kw": load,
            "meter_no": meter,
            "connection_date": fake.date_between(start_date='-5y', end_date='today'),
            "ae_details": "AE_TEST",
            "ee_details": "EE_TEST",
            "security_deposit": load * 1000,
            "ivrs_no": cid
        }
        consumers.append(c)
        
        # Smart Meter Reading (So we can bill them immediately)
        r = {
            "meter_no": meter,
            "reading_timestamp": datetime.now(),
            "kwh_cumulative": random.uniform(100, 5000),
            "kvah_cumulative": random.uniform(100, 5000),
            "voltage_r": 230.0,
            "current_r": 5.0,
            "tod_zone1": random.uniform(50, 200),
            "tod_zone2": random.uniform(50, 200),
            "tod_zone3": random.uniform(10, 50),
            "event_code": "NORMAL",
            "is_processed": False
        }
        readings.append(r)
        
        if i % 1000 == 0:
            print(f"   Generated {i} records...")

    print("2. Pushing to Database (Bulk Insert)...")
    
    # SQLAlchemy Core Bulk Insert (Fastest Method)
    session.bulk_insert_mappings(Consumer, consumers)
    session.bulk_insert_mappings(SmartMeterReading, readings)
    
    session.commit()
    session.close()
    
    duration = time.time() - start_time
    print(f"✅ DONE! Inserted {NUM_USERS} users in {duration:.2f} seconds.")

if __name__ == "__main__":
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    generate_bulk_data()