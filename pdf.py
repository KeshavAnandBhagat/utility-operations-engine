from fpdf import FPDF

class MPBillReplicaFinal(FPDF):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.set_auto_page_break(False)
        self.set_margins(7, 5, 7)
        self.set_fill_color(255, 255, 255)
        self.set_line_width(0.2)
        # Page Layout:
        # Left Margin: 7mm
        # Content Width: 196mm
        # Right Border: 203mm
        # Center Divider: 105mm (7 + 196/2)
        self.x_left = 7
        self.w_content = 196
        self.x_right_bound = 203
        self.x_mid = 105

    def header(self):
        # --- COMPANY HEADER ---
        self.rect(self.x_left, 5, self.w_content, 18)
        
        try:
            self.image('/demologo.png', 9, 7, 12) 
        except:
            self.rect(9, 7, 12, 12)
            self.set_xy(9, 10)
            self.set_font('Helvetica', 'B', 5)
            self.cell(12, 6, "LOGO", align='C')

        self.set_y(6)
        self.set_font('Helvetica', 'B', 13)
        self.cell(0, 5, self.data['company']['name'], align='C', new_x="LMARGIN", new_y="NEXT")
        
        self.set_font('Helvetica', 'B', 9)
        self.cell(0, 4, self.data['company']['address'], align='C', new_x="LMARGIN", new_y="NEXT")
        
        self.set_font('Helvetica', '', 7)
        self.cell(0, 3, self.data['company']['tagline'], align='C', new_x="LMARGIN", new_y="NEXT")
        
        self.set_xy(7, 20)
        self.set_font('Helvetica', '', 7.5)
        self.cell(50, 3, f"GST No. {self.data['company']['gst']}", align='C')
        self.cell(50, 3, f"CIN No. {self.data['company']['cin']}", align='C')
        self.cell(40, 3, f"Call Centre No. {self.data['company']['call_center']}", align='C')
        self.cell(56, 3, f"{self.data['company']['website']}", align='C')
        
        self.set_y(24)

    def draw_top_plain_section(self):
        start_y = self.get_y()
        self.set_font('Helvetica', '', 8)
        h_row = 3.5
        
        # LEFT
        self.set_xy(self.x_left, start_y + 1)
        self.cell(40, h_row, "Security Deposited:")
        self.set_xy(50, start_y + 1) 
        self.cell(25, h_row, f"INR {self.data['bill_meta']['security_deposit']}")
        
        self.set_xy(self.x_left, start_y + 1 + h_row)
        self.cell(40, h_row, "Security Deposit Pending:")
        self.set_xy(50, start_y + 1 + h_row)
        self.cell(25, h_row, "INR 0.00")
        
        self.set_xy(self.x_left, start_y + 1 + (h_row*2))
        self.cell(40, h_row, "Connection Date:")
        self.set_xy(50, start_y + 1 + (h_row*2))
        self.cell(25, h_row, str(self.data['connection']['date']))

        # RIGHT
        x_right = 100
        self.set_font('Helvetica', 'B', 8)
        
        self.set_xy(x_right, start_y + 1)
        self.cell(65, h_row, "Total Amount Payable Till Due Date:")
        self.cell(30, h_row, f"INR {self.data['financials']['total_payable']}")
        
        self.set_xy(x_right, start_y + 1 + h_row)
        self.cell(65, h_row, "Total Amount Payable After Due Date:")
        self.cell(30, h_row, f"INR {self.data['financials']['payable_after_due']}")
        
        self.set_xy(x_right, start_y + 1 + (h_row*2))
        self.cell(65, h_row, "Due Date:")
        self.cell(30, h_row, self.data['bill_meta']['due_date'])

        line_y = start_y + 12
        self.line(self.x_left, line_y, self.x_right_bound, line_y)
        self.set_y(line_y)

    def draw_consumer_box(self):
        start_y = self.get_y()
        box_height = 43.5
        self.rect(self.x_left, start_y, self.w_content, box_height)
        
        # Center Divider at 105mm (True Center)
        self.line(self.x_mid, start_y, self.x_mid, start_y + box_height)
        
        # === LEFT COLUMN ===
        self.set_xy(8, start_y + 1)
        self.set_font('Helvetica', 'B', 8)
        self.cell(35, 4, f"Consumer No. {self.data['consumer']['id']}")
        
        self.set_font('Helvetica', '', 8)
        # ALIGNMENT: ( BGH82 - 22 )
        # Divider: 105mm. Gap: 2mm. Target End X: 103mm.
        bgh_text = "( BGH82 - 22 )"
        bgh_w = self.get_string_width(bgh_text)
        self.set_xy(103 - bgh_w, start_y + 1) 
        self.cell(bgh_w, 4, bgh_text)
        
        self.set_xy(8, start_y + 5)
        self.cell(15, 4, "Purpose:")
        self.cell(60, 4, self.data['connection']['purpose'])
        
        self.set_xy(8, start_y + 9)
        self.set_font('Helvetica', 'B', 9)
        self.cell(90, 4, self.data['consumer']['id'])
        
        self.set_xy(8, start_y + 13)
        self.set_font('Helvetica', '', 8)
        self.cell(90, 4, self.data['consumer']['address'])
        
        self.set_xy(8, start_y + 21)
        self.cell(20, 4, "Mobile No.")
        self.cell(40, 4, self.data['consumer']['mobile'])
        
        self.set_xy(8, start_y + 25)
        self.cell(20, 4, "Email Id:")
        
        # Care
        y_care = start_y + 29
        self.line(self.x_left, y_care, self.x_mid, y_care)
        self.set_xy(8, y_care)
        self.cell(50, 3.5, "Customer Care Details")
        
        self.line(self.x_left, y_care + 3.5, self.x_mid, y_care + 3.5)
        self.set_xy(8, y_care + 3.5)
        self.set_font('Helvetica', 'B', 8)
        self.cell(50, 3.5, f"Call Centre No. {self.data['company']['call_center']}")
        
        self.line(self.x_left, y_care + 7, self.x_mid, y_care + 7)
        self.set_xy(8, y_care + 7)
        self.set_font('Helvetica', '', 7)
        self.cell(8, 3.5, "A.E.:")
        self.cell(60, 3.5, "MR. AE ( 9876543210 )")
        
        self.line(self.x_left, y_care + 10.5, self.x_mid, y_care + 10.5)
        self.set_xy(8, y_care + 10.5)
        self.cell(8, 3.5, "E.E.:")
        self.cell(60, 3.5, "Shri EE ( 9876543210 )")

        # === RIGHT COLUMN ===
        x_col2 = 107 # Shifted right due to 105mm divider
        
        # ALIGNMENT: Phase: SINGLE
        # Corrected to 198mm as requested
        phase_txt = f"Phase: {self.data['connection']['phase']}"
        urban_txt = "URBAN"
        
        phase_width = self.get_string_width(phase_txt)
        start_x_align = 198 - phase_width 
        
        # Row 1
        self.set_xy(x_col2, start_y + 1)
        self.set_font('Helvetica', '', 8)
        self.cell(24, 4, "Connection Type:")
        self.cell(30, 4, "Domestic ( LV1.2 )")
        
        # URBAN: Aligned with Phase
        self.set_xy(start_x_align, start_y + 1)
        self.cell(phase_width, 4, urban_txt, align='L') 
        
        # Row 2
        self.set_xy(x_col2, start_y + 5)
        self.cell(24, 4, "Sanctioned Load:")
        self.cell(30, 4, self.data['connection']['load'])
        
        # Phase: Ends at 198mm
        self.set_xy(start_x_align, start_y + 5)
        self.cell(phase_width, 4, phase_txt, align='L') 
        
        # Rest
        self.set_xy(x_col2, start_y + 9)
        self.cell(22, 4, "Meter serial No:")
        self.cell(40, 4, self.data['connection']['meter_no'])
        
        self.set_xy(x_col2, start_y + 13)
        self.set_font('Helvetica', 'B', 8)
        self.cell(18, 4, "DC / Zone:")
        self.cell(40, 4, self.data['consumer']['zone'])
        self.set_xy(x_col2, start_y + 17)
        self.set_font('Helvetica', '', 8)
        self.cell(18, 4, "Division:")
        self.cell(40, 4, "BALAGHAT")
        self.set_xy(x_col2, start_y + 21)
        self.cell(18, 4, "Feeder Code:")
        self.cell(20, 4, "3440")
        self.set_xy(x_col2, start_y + 25)
        self.cell(18, 4, "DTR Code:")
        self.cell(20, 4, "111")
        
        y_meta = start_y + 29
        self.line(self.x_mid, y_meta, self.x_right_bound, y_meta)
        
        self.set_xy(x_col2, y_meta)
        self.set_font('Helvetica', '', 8)
        self.cell(18, 3.5, "Bill No.")
        self.cell(40, 3.5, self.data['bill_meta']['bill_no'])
        self.line(self.x_mid, y_meta + 3.5, self.x_right_bound, y_meta + 3.5)
        
        self.set_xy(x_col2, y_meta + 3.5)
        self.set_font('Helvetica', 'B', 8)
        self.cell(18, 3.5, "Bill Month:")
        self.cell(40, 3.5, self.data['bill_meta']['month'])
        self.line(self.x_mid, y_meta + 7, self.x_right_bound, y_meta + 7)
        
        self.set_xy(x_col2, y_meta + 7)
        self.set_font('Helvetica', '', 8)
        self.cell(18, 3.5, "Billing Date:")
        self.cell(30, 3.5, self.data['bill_meta']['bill_date'])
        self.line(self.x_mid, y_meta + 10.5, self.x_right_bound, y_meta + 10.5)
        
        self.set_xy(x_col2, y_meta + 10.5) 
        self.cell(15, 3.5, "Bill Type:")
        self.cell(20, 3.5, "Actual Bill")
        self.set_xy(x_col2 + 55, y_meta + 10.5)
        self.cell(30, 3.5, "Read Type: NORMAL", align='R')

        self.set_y(start_y + box_height + 2)

    def draw_header_cell_centered(self, x, y, w, h, text, font_size=7):
        """Helper to draw text vertically centered in a cell"""
        self.set_xy(x, y)
        self.rect(x, y, w, h)
        
        self.set_font('Helvetica', '', font_size)
        lines = text.count('\n') + 1
        line_height = 2.5
        block_height = lines * line_height
        y_offset = (h - block_height) / 2
        
        self.set_xy(x, y + y_offset)
        self.multi_cell(w, line_height, text, align='C', border=0)

    def draw_readings(self):
        self.set_font('Helvetica', 'B', 8)
        self.write(5, "Reading Detail ")
        self.set_font('Helvetica', '', 8)
        self.write(5, "( SMART METER READ )")
        self.ln()
        
        headers = ["Current\nReading", "Current\nReading Date", "Previous\nReading", "M.F.", "Metered Unit\nConsumption", "Assessed\nUnits", "Final\nConsumption", "Average Unit\nPer Day"]
        widths = [25, 25, 25, 10, 28, 28, 28, 27] 
        
        y_start = self.get_y()
        header_h = 8
        
        for i, h in enumerate(headers):
            x = self.get_x()
            self.draw_header_cell_centered(x, y_start, widths[i], header_h, h)
            self.set_xy(x + widths[i], y_start)
        
        self.set_xy(7, y_start + header_h)
        self.set_font('Helvetica', '', 8) 
        r = self.data['readings']
        row = [r['current'], r['curr_date'], r['prev'], r['mf'], r['metered_units'], r['assessed_units'], r['final_units'], r['avg_unit_day']]
        
        for i, val in enumerate(row):
            self.cell(widths[i], 5, str(val), border=1, align='C')
        self.ln(6)

    def draw_full_width_payment(self):
        self.set_font('Helvetica', 'B', 8)
        self.cell(0, 4, "Last Payment Detail", new_x="LMARGIN", new_y="NEXT")
        
        headers = ["Bill Month", "Amount Paid", "Payment Reference No.", "Payment Date"]
        widths = [25, 30, 101, 40] 
        
        self.set_font('Helvetica', '', 7)
        for i, h in enumerate(headers):
            self.cell(widths[i], 4, h, border=1, align='C')
        self.ln()
        
        for pay in self.data['last_payments']:
            self.cell(widths[0], 4, pay['month'], border=1, align='C')
            self.cell(widths[1], 4, pay['amount'], border=1, align='R')
            self.cell(widths[2], 4, pay.get('ref', '-'), border=1, align='L')
            self.cell(widths[3], 4, pay['date'], border=1, align='C')
            self.ln()
        self.ln(1)

    def draw_middle_split(self):
        start_y = self.get_y()
        x_right_col = 95
        
        self.set_xy(x_right_col, start_y)
        self.set_font('Helvetica', 'B', 8)
        self.cell(78, 4, "Billing Details", border=1, align='C')
        self.cell(30, 4, "Amount in INR", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
        
        fin = self.data['financials']
        def add_fin_row(label, value, bold=False):
            self.set_x(x_right_col)
            if bold: self.set_font('Helvetica', 'B', 8)
            else: self.set_font('Helvetica', '', 8)
            
            if len(label) > 40:
                x = self.get_x()
                y = self.get_y()
                self.multi_cell(78, 3.5, label, border=1, align='L')
                h = self.get_y() - y
                self.set_xy(x + 78, y)
                self.cell(30, h, str(value), border=1, align='R')
                self.set_xy(7, y + h)
            else:
                self.cell(78, 3.5, label, border=1)
                self.cell(30, 3.5, str(value), border=1, align='R')
                self.set_xy(7, self.get_y() + 3.5)

        add_fin_row("Energy Charges", fin['energy_chg'])
        add_fin_row("Fuel and Power Purchase Adjustment Surcharge", fin['fppas'])
        add_fin_row("Fixed Charge", fin['fixed_chg'])
        add_fin_row("Electricity Duty", fin['duty'])
        add_fin_row("Additional SD Installment", fin['addl_sd'])
        add_fin_row("Other / TOD Rebate", fin['tod_adj'])
        add_fin_row("Month Bill Amount", fin['month_bill_amt'])
        add_fin_row("M.P. Govt. Subsidy Amount", fin['subsidy'], bold=True)
        add_fin_row("Interest On Security Deposit (-)", fin['sd_interest'])
        add_fin_row("CCB Adjustment", "0.00")
        add_fin_row("Lock Credit / Employee Rebate (-)", "0.00")
        add_fin_row("Online / Advance Payment Incentive (-)", fin['online_incentive'])
        add_fin_row("Current Month Bill Amount", fin['curr_bill_amt'], bold=True)
        add_fin_row("Principal Arrear", fin['arrears'])
        add_fin_row("Cumulative Surcharge", "0.00")
        add_fin_row("ASD Arrear", "0.00")
        add_fin_row("Amount Received against Bill & Vigilance", fin['amt_received'])
        add_fin_row("Smart Meter RC/DC Amount Received", "0.00")
        add_fin_row("Vigilance / O&M Due Amount", "0.00")
        add_fin_row("Interest on Vigilance / O&M Due (Till Billing Period)", "0.00")
        add_fin_row("Total Amount Payable", fin['total_payable'], bold=True)
        
        right_end_y = self.get_y()

        self.set_xy(7, start_y)
        w_left = 85
        
        self.set_font('Helvetica', 'B', 8)
        self.cell(w_left, 4, "Last Six Months Consumption", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('Helvetica', '', 7)
        self.cell(20, 3.5, "Bill Month", border=1, align='C')
        self.cell(25, 3.5, "Date", border=1, align='C')
        self.cell(20, 3.5, "Reading", border=1, align='C')
        self.cell(20, 3.5, "Unit", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
        
        for idx, hist in enumerate(self.data['consumption_history']):
            if idx == len(self.data['consumption_history']) - 1:
                self.set_font('Helvetica', 'B', 7)
            else:
                self.set_font('Helvetica', '', 7)
            self.cell(20, 3.5, hist['month'], border=1, align='C')
            self.cell(25, 3.5, hist['date'], border=1, align='C')
            self.cell(20, 3.5, hist['reading'], border=1, align='R')
            self.cell(20, 3.5, hist['units'], border=1, align='R', new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

        self.set_font('Helvetica', 'B', 8)
        self.cell(w_left, 4, "Vigilance / O&M Panchnama Detail", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('Helvetica', '', 7)
        self.cell(60, 3.5, "Description", border=1, align='C')
        self.cell(25, 3.5, "Amount", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
        for _ in range(4):
            self.cell(60, 3.5, "", border=1)
            self.cell(25, 3.5, "", border=1, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

        self.set_font('Helvetica', 'B', 8)
        self.cell(w_left, 4, "TOD Consumption Detail", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('Helvetica', '', 7)
        self.cell(25, 3.5, "Description", border=1, align='L') 
        self.cell(25, 3.5, "", border=1, align='L')
        self.cell(15, 3.5, "Unit", border=1, align='C')
        self.cell(20, 3.5, "Rebate", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
        
        for tod in self.data['tod_data']:
            self.cell(25, 3.5, tod['desc'], border=1, align='L') 
            self.cell(25, 3.5, tod['time'], border=1, align='C') 
            self.cell(15, 3.5, tod['units'], border=1, align='C')
            self.cell(20, 3.5, tod['rebate'], border=1, align='R', new_x="LMARGIN", new_y="NEXT")

        self.set_y(max(self.get_y(), right_end_y) + 1)

    def draw_footer_section(self):
        start_y = self.get_y()
        
        # Table starts at 75 (Wider)
        x_table = 75 
        w_table = 128
        
        self.set_xy(x_table, start_y)
        self.set_font('Helvetica', 'B', 8)
        self.cell(w_table, 4, "Meter Replacement and Read Detail", border=1, align='C', new_x="LMARGIN", new_y="NEXT")
        
        # Headers
        self.set_x(x_table)
        headers = ["Meter Detail", "Prev / Start\nRead", "Final / Current\nRead", "Consumption", "Prorated Current\nBill"]
        widths = [30, 22, 22, 22, 32]
        header_h = 9
        
        for i, h in enumerate(headers):
            x = self.get_x()
            self.draw_header_cell_centered(x, start_y + 4, widths[i], header_h, h)
            self.set_xy(x + widths[i], start_y + 4)
            
        # Rows
        self.set_xy(x_table, start_y + 4 + header_h)
        
        # Row 1 (5mm)
        for w in widths:
            self.cell(w, 5, "", border=1)
        self.ln()
        
        # Row 2 (7.5mm)
        self.set_x(x_table)
        for w in widths:
            self.cell(w, 7.5, "", border=1)
        
        # Left Empty Box: Narrower
        self.rect(7, start_y, 68, 25.5)

    def generate(self, filename="MPEZ_Final_Replica.pdf"):
        self.add_page()
        self.header()
        self.draw_top_plain_section()
        self.draw_consumer_box()
        self.draw_readings()
        self.draw_full_width_payment()
        self.draw_middle_split()
        self.draw_footer_section()
        self.output(filename)
        print(f"✅ Final Perfect Replica Generated: {filename}")

