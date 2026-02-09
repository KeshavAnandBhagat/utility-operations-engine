from sqlalchemy.orm import Session
from models import SessionLocal, Consumer, Bill,SmartMeterReading

def get_db():
    """Helper to get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- CONSUMER OPERATIONS ---

def create_consumer(data: dict):
    db = SessionLocal()
    # Check if exists
    existing = db.query(Consumer).filter(Consumer.id == data['id']).first()
    if existing:
        print(f"⚠️ Consumer {data['id']} already exists.")
        db.close()
        return existing
    
    new_consumer = Consumer(**data)
    db.add(new_consumer)
    db.commit()
    db.refresh(new_consumer)
    print(f"✅ Created Consumer: {new_consumer.name}")
    db.close()
    return new_consumer

def get_consumer(consumer_id: str):
    db = SessionLocal()
    consumer = db.query(Consumer).filter(Consumer.id == consumer_id).first()
    db.close()
    return consumer

# --- BILL OPERATIONS ---

def get_last_bill(consumer_id):
    db = SessionLocal()
    last_bill = db.query(Bill)\
        .filter(Bill.consumer_id == consumer_id)\
        .order_by(Bill.bill_id.desc())\
        .first()
    db.close()
    return last_bill

# 2. GET LATEST SMART METER READING (To find Current Reading)
def get_latest_smart_reading(meter_no):
    db = SessionLocal()
    reading = db.query(SmartMeterReading)\
        .filter(SmartMeterReading.meter_no == meter_no)\
        .order_by(SmartMeterReading.reading_timestamp.desc())\
        .first()
    db.close()
    return reading

# 3. SAVE THE NEW BILL
def save_bill_record(bill_data):
    db = SessionLocal()
    new_bill = Bill(**bill_data)
    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)
    db.close()
    print(f"✅ Bill Saved to DB successfully! Bill ID: {new_bill.bill_id}")
    return new_bill

def get_all_consumer_ids():
    """Fetches ALL consumer IDs for batch processing"""
    db = SessionLocal()
    # In a real app, you might filter by active status or zone
    # users = db.query(Consumer.id).filter(Consumer.is_active == True).all()
    users = db.query(Consumer.id).all()
    db.close()
    # Returns a list of tuples like [('N100...'), ('N200...')], so we flatten it
    return [u[0] for u in users]