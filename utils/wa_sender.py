import requests
import os
import time
import random

# Load token dari environment variable
TOKEN = os.getenv("META_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")

def send_message(phone, name, template_text):
    """
    phone: 6281xxxx
    name: Fulan
    template_text: "Halo {Name}, apa kabar?"
    """
    
    # 1. Replace variable
    final_message = template_text.replace("{Name}", name)
    
    # 2. Prepare Payload Meta
    url = f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": final_message}
    }
    
    # 3. Send Request
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return True, "Sent"
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)