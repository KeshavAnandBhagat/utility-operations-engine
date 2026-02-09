import datetime
import repo
from calc import calculate_bill_industrial_final
from pdf import MPBillReplicaFinal
import random

def generate_invoice(consumer_id, manual_prev_reading=None):
    """
    Fully Automated Billing Cycle:
    1. DB: Fetch Consumer Profile
    2. DB: Fetch Current Smart Meter Reading
    3. DB: Fetch Previous Bill (for prev reading)
    4. Logic: Calculate
    5. PDF: Generate
    6. DB: Save Result
    """
    print(f"--- 🚀 Starting Billing Process for: {consumer_id} ---")

    # --- 1. FETCH CONSUMER ---
    consumer = repo.get_consumer(consumer_id)
    if not consumer:
        print(f"❌ Error: Consumer {consumer_id} not found.")
        return

    # --- 2. FETCH CURRENT READING (From Smart Meter) ---
    print(f"🔎 Looking for Smart Meter data (Meter: {consumer.meter_no})...")
    smart_data = repo.get_latest_smart_reading(consumer.meter_no)
    
    if smart_data:
        current_reading = smart_data.kwh_cumulative
        # For demo, we assume TOD units come from the meter. 
        # In reality, you'd calculate (Current_TOD - Prev_TOD)
        tod_units = int(smart_data.tod_zone3) 
        print(f"   ✅ Found Smart Reading: {current_reading} kWh")
    else:
        print("   ❌ No Smart Meter data found! Cannot proceed.")
        return

    # --- 3. FETCH PREVIOUS READING (From Bill History) ---
    print("🔎 Fetching Previous Bill...")
    last_bill = repo.get_last_bill(consumer_id)
    
    if last_bill:
        prev_reading = last_bill.current_reading
        print(f"   ✅ Found Previous Bill. Prev Reading: {prev_reading}")
    else:
        # Fallback logic
        if manual_prev_reading is not None:
            prev_reading = manual_prev_reading
            print(f"   ⚠️ No history found. Using Parameter: {prev_reading}")
        else:
            prev_reading = 0.0
            print("   ⚠️ No history found. Defaulting to 0.0")

    # --- 4. CALCULATE ---
    print("🧮 Calculating Financials...")
    
    # Example Config
    current_fca_config = [{"days": 31, "rate": 1.05}]
    bill_days = 31

    calc_results = calculate_bill_industrial_final(
        current_reading=current_reading,
        prev_reading=prev_reading,
        tod_units=tod_units,
        security_deposit_amt=consumer.security_deposit,
        bill_days=bill_days,
        fca_config=current_fca_config,
        last_bill_amount=last_bill.total_payable if last_bill else 0
    )

    # --- 5. GENERATE PDF ---
    print("📄 Generating PDF Document...")
    
    # Financial Helpers
    total_payable = float(calc_results['total'])
    payable_after_due = total_payable * 1.013
    bill_month_str = datetime.date.today().strftime("%b-%Y").upper() # e.g., FEB-2026
    
    pdf_payload = {
        "company": {
            "name": "MP Eastern Power Distribution Services (DEMO)",
            "address": "Sample Tower, City Centre, MP",
            "tagline": "(Fictional Utility For Educational Use Only)",
            "gst": "26AAAAA0000A1Z5", "cin": "U00000MP2025PLC000000", 
            "call_center": "1800-000-0000", "website": "http://www.samplepowerdemo.in"
        },
        "consumer": {
            "id": consumer.id, "name": consumer.name,
            "address": consumer.address, "mobile": consumer.mobile, "zone": consumer.zone
        },
        "connection": {
            "date": str(consumer.connection_date),
            "load": f"{consumer.load_kw} KW",
            "phase": consumer.phase,
            "purpose": consumer.purpose,
            "meter_no": consumer.meter_no
        },
        "bill_meta": {
            "month": bill_month_str,
            "bill_date": datetime.date.today().strftime("%d-%m-%Y"),
            "due_date": (datetime.date.today() + datetime.timedelta(days=15)).strftime("%d-%m-%Y"),
            "bill_no": f"BILL-{consumer_id[-4:]}-{datetime.date.today().month}",
            "security_deposit": str(consumer.security_deposit)
        },
        "readings": {
            "current": str(current_reading),
            "curr_date": datetime.date.today().strftime("%d-%m-%Y"),
            "prev": str(prev_reading),
            "mf": "1",
            "metered_units": calc_results['units_consumed'],
            "assessed_units": "0.00",
            "final_units": calc_results['units_consumed'],
            "avg_unit_day": f"{float(calc_results['units_consumed'])/bill_days:.2f}"
        },
        "last_payments": [], # Can be fetched from DB similarly if needed
        "consumption_history": [],
        "tod_data": [
             {"desc": "Off Peak", "time": "9 AM - 5 PM", "units": str(tod_units), "rebate": calc_results['tod_rebate']},
             {"desc": "Peak", "time": "5 PM - 10 PM", "units": "0", "rebate": "0.00"}
        ],
        "financials": {
            "energy_chg": calc_results['energy_charge'],
            "fppas": calc_results['fca_weighted'],
            "fixed_chg": calc_results['fixed_charge'],
            "duty": calc_results['duty'],
            "addl_sd": "0",
            "tod_adj": f"-{calc_results['tod_rebate']}",
            "month_bill_amt": calc_results['total'],
            "subsidy": "0.00",
            "sd_interest": calc_results['sd_credit'],
            "online_incentive": calc_results['online_incentive'],
            "curr_bill_amt": calc_results['total'],
            "arrears": "0.00",
            "amt_received": "0.00",
            "total_payable": calc_results['total'],
            "payable_after_due": f"{payable_after_due:.2f}"
        }
    }

    pdf = MPBillReplicaFinal(pdf_payload)
    pdf_filename = f"Bill_{consumer_id}_{bill_month_str}.pdf"
    pdf.generate(pdf_filename)

    # --- 6. SAVE TO DATABASE ---
    print("💾 Saving Bill Record to Database...")
    
    # We map our calculation results to the SQLAlchemy 'Bill' model
    db_record = {
        # --- IDENTITY & DATES ---
        "bill_no": pdf_payload['bill_meta']['bill_no'],
        "consumer_id": consumer_id,
        "bill_month": bill_month_str,
        "bill_date": datetime.date.today(),
        "due_date": datetime.date.today() + datetime.timedelta(days=15),
        "reading_date": datetime.date.today(), # <--- Missing in your previous code
        
        # --- READINGS ---
        "prev_reading": float(prev_reading),
        "current_reading": float(current_reading),
        "metered_units": float(calc_results['units_consumed']), # <--- Renamed from 'units_consumed'
        "total_units": float(calc_results['units_consumed']),   # <--- Renamed
        "avg_reading_type": "NORMAL",                           # <--- Required by DB
        
        # --- FINANCIALS ---
        "energy_charge": float(calc_results['energy_charge']),
        "fixed_charge": float(calc_results['fixed_charge']),
        "fppas_amount": float(calc_results['fca_weighted']),
        "electricity_duty": float(calc_results['duty']),        # <--- Renamed from 'duty'
        "tod_rebate": float(calc_results['tod_rebate']),
        "sd_interest_credit": float(calc_results['sd_credit']), # <--- Added
        "online_incentive": float(calc_results['online_incentive']), # <--- Added
        
        # --- TOTALS ---
        "net_current_bill": float(calc_results['total']),       # <--- Added
        "arrears": 0.0,
        "total_payable": float(calc_results['total']),
        "payable_after_due": float(f"{payable_after_due:.2f}"), # <--- Added
        
        # --- JSON COLUMNS (The System Design Logic) ---
        # 1. Store TOD Data
        "tod_readings": pdf_payload['tod_data'], 
        
        # 2. Store Configuration in 'applied_tariff' instead of 'fca_config'
        "applied_tariff": {
            "fca_config": current_fca_config,
            "bill_days": bill_days
        },
        
        # 3. History (Optional)
        "consumption_history": [],
        "payment_history": []
    }
    
    repo.save_bill_record(db_record)
    print("✅ Process Complete.")

# --- EXECUTION ---
if __name__ == "__main__":
    # Ensure you have seeded:
    # 1. Consumer (N100...)
    # 2. Smart Meter Reading (SCHNEIDEREZ...)
    
    generate_invoice(consumer_id="N1009876543")