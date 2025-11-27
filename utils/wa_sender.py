import requests
import os
import json

def send_template_to_meta(phone, template_name, parameters=None):
    """
    Mengirim Template Message (Wajib untuk inisiasi chat).
    parameters: list of strings (misal ['Budi', '80']) untuk {{1}}, {{2}}
    """
    token = os.getenv("META_TOKEN")
    phone_id = os.getenv("PHONE_NUMBER_ID")
    version = os.getenv("API_VERSION", "v17.0")
    
    url = f"https://graph.facebook.com/{version}/{phone_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Construct Components (Variables)
    components = []
    if parameters:
        body_params = []
        for param in parameters:
            body_params.append({
                "type": "text",
                "text": str(param)
            })
        
        components.append({
            "type": "body",
            "parameters": body_params
        })

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "id"}, # Sesuaikan dengan setting di Meta (id/en_US)
            "components": components
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)