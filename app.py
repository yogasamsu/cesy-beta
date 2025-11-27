import streamlit as st
import pandas as pd
import requests
import time
import random

# --- CONFIGURATION (Nanti dipindah ke .env untuk keamanan) ---
# Paste Token & ID dari Meta Dashboard di sini:
META_TOKEN = "PASTE_TOKEN_PANJANG_ANDA_DISINI_EAAG..." 
PHONE_NUMBER_ID = "PASTE_PHONE_ID_ANDA_DISINI" 

# Versi API Meta
API_VERSION = "v17.0"

st.set_page_config(page_title="Cesy - HSI Edu", page_icon="🕌")

# --- UI HEADER ---
st.title("🕌 Cesy: HSI Campaign Blaster")
st.markdown("Customer Engagement System untuk **HSI Edu** (MVP Version)")
st.divider()

# --- FUNGSI PENGIRIM (ENGINE) ---
def send_template_message(phone, template_name="hello_world", language="en_US"):
    url = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {META_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Payload KHUSUS Template (Aturan Meta)
    data = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": language
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

# --- BAGIAN 1: UPLOAD DATA ---
st.subheader("1. Upload Data Peserta")
uploaded_file = st.file_uploader("Upload file CSV (Kolom: Name, Phone)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Cleaning Data: Pastikan nomor HP jadi string
    df['Phone'] = df['Phone'].astype(str)
    
    # Cleaning Data: Pastikan format 62 (bukan 08)
    def clean_phone(num):
        num = num.strip().replace("-", "").replace(" ", "")
        if num.startswith("0"):
            return "62" + num[1:]
        if num.startswith("8"):
            return "62" + num
        return num

    df['Phone'] = df['Phone'].apply(clean_phone)
    
    st.dataframe(df)
    st.info(f"✅ Siap mengirim ke {len(df)} kontak.")

    # --- BAGIAN 2: PILIH TEMPLATE ---
    st.subheader("2. Konfigurasi Pesan")
    st.warning("⚠️ Karena aturan Meta, Blast harus menggunakan Template.")
    
    # Dropdown Template
    template_choice = st.selectbox(
        "Pilih Template Pesan:",
        ["hello_world (Test Default)", "hsi_promo (Custom - Belum Dibuat)"]
    )
    
    if template_choice == "hello_world (Test Default)":
        st.code("Template Content: Welcome and congratulations. This message demonstrates your ability to send a message notification...", language="text")
        actual_template_name = "hello_world"
    else:
        st.error("Template ini belum dibuat di Meta Dashboard. Pilih hello_world dulu.")
        actual_template_name = "hsi_promo"

    # --- BAGIAN 3: EKSEKUSI ---
    st.subheader("3. Eksekusi Blast")
    
    if st.button("🚀 KIRIM PESAN SEKARANG"):
        if not META_TOKEN or "PASTE" in META_TOKEN:
            st.error("❌ Token belum diisi di code! Edit file app.py dulu.")
        else:
            progress_bar = st.progress(0)
            log_area = st.empty()
            
            success = 0
            failed = 0
            
            for index, row in df.iterrows():
                # Update UI Log
                log_area.text(f"⏳ Mengirim ke {row['Name']} ({row['Phone']})...")
                
                # Kirim
                status, response = send_template_message(
                    phone=row['Phone'], 
                    template_name=actual_template_name
                )
                
                if status:
                    success += 1
                else:
                    failed += 1
                    st.toast(f"Gagal ke {row['Name']}: {response}")
                
                # Update Progress
                progress_bar.progress((index + 1) / len(df))
                
                # JEDA (PENTING AGAR TIDAK BANNED)
                time.sleep(random.uniform(1.5, 3.0))
            
            st.success(f"🎉 Selesai! Berhasil: {success}, Gagal: {failed}")