import math
from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR

def calculate_bill_industrial_final(current_reading, prev_reading, tod_units, security_deposit_amt, bill_days, fca_config, last_bill_amount):
    # --- Helper: Currency Rounding (2 Decimal Places) ---
    def round_currency(value):
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # --- Helper: Duty Specific Rounding (Integer) ---
    # "Fractions of 0.5 or above are rounded up... less than 0.5 are ignored."
    def round_duty_special(value):
        # Logic: x + 0.5, then floor. 
        # Ex: 24.4 + 0.5 = 24.9 -> 24.  |  24.5 + 0.5 = 25.0 -> 25.
        val = float(value)
        return Decimal(math.floor(val + 0.5))

    # --- 1. CONSUMPTION ---
    units = Decimal(str(current_reading)) - Decimal(str(prev_reading))
    
    # --- 2. FIXED CHARGES ---
    fixed_rate_slab1 = Decimal('76.00')
    fixed_rate_slab2 = Decimal('129.00')
    fixed_rate_per_0_1kw = Decimal('28.00')

    if units <= 50:
        raw_fixed = fixed_rate_slab1
    elif units <= 150:
        raw_fixed = fixed_rate_slab2
    else:
        chunks = Decimal(math.ceil(units / 15))
        raw_fixed = chunks * fixed_rate_per_0_1kw
    
    fixed_charge = round_currency(raw_fixed)

    # --- 3. ENERGY CHARGE (Base) ---
    energy_rates = [Decimal('4.45'), Decimal('5.41'), Decimal('6.79'), Decimal('6.98')]
    energy_charge_total = Decimal('0.00')
    rem_units = units
    
    # Standard Slabs
    slabs = [(50, 0), (100, 1), (150, 2), (float('inf'), 3)]
    
    for limit, idx in slabs:
        if rem_units <= 0: break
        slab_u = min(rem_units, Decimal(limit))
        energy_charge_total += slab_u * energy_rates[idx]
        rem_units -= slab_u
        
    energy_charge = round_currency(energy_charge_total)

    # --- 4. WEIGHTED FCA ---
    total_fca_precise = Decimal('0.0000')
    
    if fca_config and bill_days > 0:
        for segment in fca_config:
            days = Decimal(segment['days'])
            rate = Decimal(str(segment['rate'])) # This is a %
            
            # Pro-rata Energy * Rate%
            part_energy = energy_charge * (days / Decimal(bill_days))
            part_fca = part_energy * (rate / Decimal('100'))
            total_fca_precise += part_fca
            
    fca_final = round_currency(total_fca_precise)

    # --- 5. DUTY CALCULATION (The Update) ---
    # Step A: Find Average FCA per Unit to apportion it
    if units > 0:
        avg_fca_per_unit = total_fca_precise / units
    else:
        avg_fca_per_unit = Decimal('0.00')

    duty_pct_low = Decimal('0.09')  # 9%
    duty_pct_high = Decimal('0.12') # 12%
    
    duty_precise_total = Decimal('0.00')
    rem_units_duty = units
    
    # Duty Slabs: 0-100 @ 9%, >100 @ 12%
    # We must match the Energy Rate slabs to calculate accurate base cost
    # Slabs: Limit, Energy_Rate, Duty_Pct
    duty_slabs = [
        (50,  energy_rates[0], duty_pct_low),  # 0-50:   Rate 4.45 + FCA, Duty 9%
        (50,  energy_rates[1], duty_pct_low),  # 51-100: Rate 5.41 + FCA, Duty 9%
        (50,  energy_rates[1], duty_pct_high), # 101-150: Rate 5.41 + FCA, Duty 12%
        (150, energy_rates[2], duty_pct_high), # 151-300: Rate 6.79 + FCA, Duty 12%
        (float('inf'), energy_rates[3], duty_pct_high) # 300+: Rate 6.98 + FCA, Duty 12%
    ]

    for limit, rate_val, pct in duty_slabs:
        if rem_units_duty <= 0: break
        current_slab_units = min(rem_units_duty, Decimal(limit))
        
        # Base Cost for this slab (Energy + Proportioned FCA)
        # Note: We add the FCA component to the Energy component
        slab_base_cost = (current_slab_units * rate_val) + (current_slab_units * avg_fca_per_unit)
        
        # Calculate Duty on this adjusted base
        chunk_duty = slab_base_cost * pct
        
        duty_precise_total += chunk_duty
        rem_units_duty -= current_slab_units

    # Apply Special Rounding (0.5 Rule)
    duty_final = round_duty_special(duty_precise_total)

    # --- 6. TOD REBATE ---
    if units > 0:
        eff_rate = energy_charge / units
    else:
        eff_rate = Decimal('0.00')
    tod_rebate = round_currency(Decimal(tod_units) * eff_rate * Decimal('0.20'))

    # --- 7. INTEREST ---
    rate = Decimal('6.62245381')
    monthly_sd_interest = (Decimal(security_deposit_amt) * (rate / 100)) / 12
    sd_credit = round_currency(monthly_sd_interest)

    # --- 8. ONLINE INCENTIVE (New Addition) ---
    # Rule: 0.5% of Last Bill Amount, Min ₹5.00
    calc_incentive = Decimal(str(last_bill_amount)) * Decimal('0.005')
    
    if calc_incentive < Decimal('5.00'):
        raw_incentive = Decimal('5.00')
    else:
        raw_incentive = calc_incentive
        
    online_incentive = round_currency(raw_incentive)

    # --- 9. TOTAL ---
    # Subtract online_incentive from the total
    total_amount = fixed_charge + energy_charge + fca_final + duty_final - tod_rebate - sd_credit - online_incentive
    month_bill_amt=  fixed_charge + energy_charge + fca_final + duty_final - tod_rebate
    return {
        "fixed_charge": str(fixed_charge),
        "energy_charge": str(energy_charge),
        "fca_weighted": str(fca_final),
        "duty": str(duty_final),
        "tod_rebate": str(tod_rebate),
        "month_bill_amt": str(month_bill_amt),  
        "sd_credit": str(sd_credit),
        "online_incentive": str(online_incentive), # New field
        "total": str(total_amount),
        "units_consumed": str(units),
        "debug_avg_fca_unit": str(avg_fca_per_unit)
    }

# --- TEST USAGE ---
fca_data = [
    {"days": 22, "rate": -2.23},
    {"days": 9, "rate": 1.05}
]

# Last bill amount (e.g. 3117 from your previous bill)
# print(calculate_bill_industrial_final(
#     current_reading=6856.93, 
#     prev_reading=6478.11, 
#     tod_units=109, 
#     security_deposit_amt=4677,
#     bill_days=31,
#     fca_config=fca_data,
#     last_bill_amount=3235.00

# ))

# print(calculate_bill_industrial_final(
#     current_reading=24.25, 
#     prev_reading=0, 
#     tod_units=0, 
#     security_deposit_amt=1000.00,
#     bill_days=31,
#     fca_config=fca_data,
#     last_bill_amount=0

# ))