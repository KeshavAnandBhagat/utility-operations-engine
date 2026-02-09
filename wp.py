import requests

def send_whatsapp_bill(mobile_no, pdf_link, amount, month):
    TOKEN = "..."
    PHONE_NUMBER_ID = "...."
    TO = "...." 
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": mobile_no,
        "type": "template",
        "template": {
            "name": "utility_bill_alert",  # You create this in FB dashboard
            "language": {"code": "en"},
            "components": [
                {
                    "type": "header",
                    "parameters": [{
                        "type": "document",
                        "document": {
                            "link": pdf_link,
                            "filename": "MPEZ_Bill.pdf"
                        }
                    }]
                },
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": month},  # {{1}}
                        {"type": "text", "text": amount}  # {{2}}
                    ]
                }
            ]
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print(response.json())
    return response.json()


send_whatsapp_bill(...., "www.google.com", 100, "Test")