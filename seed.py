from sqlalchemy.orm import Session
from models import engine, Consumer, SystemConfig
from datetime import date

session = Session(bind=engine)

# 1. Setup Company Config (The Static Header Info)
if not session.query(SystemConfig).first():
    config = SystemConfig(
        company_name="MP Eastern Power Distribution Services (DEMO)",
        address="Sample Tower, City Centre, MP",
        gst_no="26AAAAA0000A1Z5",
        cin_no="U00000MP2025PLC000000",
        call_center_no="1800-000-0000",
        website="http://www.samplepowerdemo.in/"
    )
    session.add(config)

# 2. Setup The Consumer (With AE/EE/Feeder details)
# Check if exists first to avoid duplicates
existing = session.query(Consumer).filter_by(id="N1009876543").first()
if not existing:
    user = Consumer(
        id="N1009876543",
        old_service_no="( ABC )",
        name="Keshav",
        address="BALAGHAT",
        mobile="94*****757",
        
        # Location & Grid
        zone="Balaghat(T)",
        division="BALAGHAT",
        dc_code="--", # Add real code if you have it
        feeder_code="3440",
        dtr_code="111",
        
        # Connection
        connection_type="Domestic ( LV1.2 )",
        purpose="Domestic light and fan",
        phase="SINGLE",
        load_kw=2.0,
        meter_no="SCHNEIDERE123",
        connection_date=date(2021, 2, 5),
        
        # Officers (The new requirement)
        ae_details="AE",
        ee_details="EE",
        
        security_deposit=3809.00
    )
    session.add(user)
    print("✅ Consumer Seeded with AE/EE Details")

session.commit()
session.close()