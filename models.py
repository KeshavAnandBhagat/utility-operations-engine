from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, JSON, Boolean,DateTime
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import date
import datetime

# --- SETUP ---
# Used SQLite for now. For Resume: "Designed for PostgreSQL 15+"
DATABASE_URL = "sqlite:///billing_system.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# --- 1. SYSTEM CONFIGURATION (Singleton Table) ---
# Stores Company Details (CIN, GST, Call Center)
class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True)
    company_name = Column(String) # "M.P. Poorv Kshetra..."
    address = Column(String)
    gst_no = Column(String)
    cin_no = Column(String)
    call_center_no = Column(String) # "1912"
    website = Column(String)

# --- 2. CONSUMER MASTER (The Entity) ---
class Consumer(Base):
    __tablename__ = "consumers"

    # Identity
    id = Column(String, primary_key=True) # "N1001036640" (Consumer No)
    old_service_no = Column(String)       # "( BGH82 - 22 )"
    name = Column(String, nullable=False)
    address = Column(String)
    mobile = Column(String)
    email = Column(String, nullable=True)
    
    # Hierarchy / Location
    zone = Column(String)      # "Balaghat(T)"
    division = Column(String)  # "BALAGHAT"
    dc_code = Column(String)   # Distribution Center Code
    
    # Technical Grid Details (The missing link!)
    feeder_code = Column(String) # "3440"
    dtr_code = Column(String)    # "111"
    
    # Connection Params
    connection_type = Column(String) # "Domestic ( LV1.2 )"
    purpose = Column(String)         # "Domestic light and fan"
    phase = Column(String)           # "SINGLE" or "THREE"
    load_kw = Column(Float)          # 2.0
    meter_no = Column(String)        # "SCHNEIDEREZ0410851"
    connection_date = Column(Date)
    
    # Officials (Attached to Consumer's Zone)
    # Storing names here implies "Current Officer for this user"
    ae_details = Column(String) # ""
    ee_details = Column(String) # ""
    
    # Financial Base
    security_deposit = Column(Float) # 3809.00

    bills = relationship("Bill", back_populates="consumer")

# --- 3. BILL LEDGER (The Transaction) ---
class Bill(Base):
    __tablename__ = "bills"

    bill_id = Column(Integer, primary_key=True, autoincrement=True)
    bill_no = Column(String, unique=True, index=True) # "JUL25N00..."
    consumer_id = Column(String, ForeignKey("consumers.id"))
    
    # --- DATES ---
    bill_month = Column(String) # "JUL-2025"
    bill_date = Column(Date)
    due_date = Column(Date)
    
    # --- READINGS ---
    reading_date = Column(Date)
    current_reading = Column(Float)
    prev_reading = Column(Float)
    multiplying_factor = Column(Float, default=1.0)
    metered_units = Column(Float)
    assessed_units = Column(Float, default=0.0)
    total_units = Column(Float) # Final Consumption
    avg_reading_type = Column(String) # "NORMAL"
    
    # --- FINANCIAL SNAPSHOT (The "System Design" Fix) ---
    # We store the RATES used for this specific bill here.
    # This ensures if rates change next month, this bill record remains historically accurate.
    applied_tariff = Column(JSON) 
    # Structure: {
    #   "fca_rate": 0.15,
    #   "duty_rate": 0.09,
    #   "fixed_rate_slab": {"0-50": 76, "50+": 129},
    #   "energy_rate_slab": {"0-50": 4.45, ...},
    #   "sd_interest_rate": 6.196
    # }

    # --- CALCULATED COSTS ---
    energy_charge = Column(Float)
    fixed_charge = Column(Float)
    fppas_amount = Column(Float)
    electricity_duty = Column(Float)
    tod_rebate = Column(Float)
    sd_interest_credit = Column(Float)
    online_incentive = Column(Float)
    
    # --- TOTALS ---
    net_current_bill = Column(Float)
    arrears = Column(Float)
    total_payable = Column(Float)
    payable_after_due = Column(Float) # Includes surcharge

    # --- COMPLEX DATA ---
    tod_readings = Column(JSON) # List of TOD slots
    payment_history = Column(JSON) # Last 2-3 payments snapshot
    consumption_history = Column(JSON) # Last 6 months snapshot

    consumer = relationship("Consumer", back_populates="bills")

class SmartMeterReading(Base):
    __tablename__ = "smart_meter_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    meter_no = Column(String, ForeignKey("consumers.meter_no"), index=True)
    
    # When did the meter record this? (The timestamp inside the meter)
    reading_timestamp = Column(DateTime, nullable=False) 
    
    # When did our server receive it? (Audit trail)
    received_at = Column(DateTime, default=datetime.datetime.now)
    
    # 1. CUMULATIVE (The "Odometer")
    kwh_cumulative = Column(Float) # 6856.93
    kvah_cumulative = Column(Float) 
    
    # 2. INSTANTANEOUS (The "Speedometer")
    voltage_r = Column(Float) # 230.5
    current_r = Column(Float) # 4.2
    
    # 3. TOD BUCKETS (Derived from Load Profile)
    # The meter sends distinct registers for Zone 1, Zone 2, Zone 3
    tod_zone1 = Column(Float) # Off Peak
    tod_zone2 = Column(Float) # Normal
    tod_zone3 = Column(Float) # Peak
    
    # 4. EVENTS (Tamper detection)
    event_code = Column(String) # "Magnet Tamper", "Cover Open"

    # Status
    is_processed = Column(Boolean, default=False)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Complete Billing Schema Created (Consumers, Bills, Config)")

if __name__ == "__main__":
    init_db()