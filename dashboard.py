import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv
from utils.csv_helper import process_csv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Cesy HSI", layout="wide")

st.title("🕌 Cesy: HSI Engagement")
st.markdown("---")

# TABS
tab1, tab2 = st.tabs(["🚀 New Campaign", "📊 History Log"])

with tab1:
    st.subheader("1. Upload Target")
    uploaded_file = st.file_uploader("Upload CSV (Name, Phone)", type="csv")
    
    if uploaded_file:
        df_clean, msg = process_csv(uploaded_file)
        
        if df_clean is not None:
            st.success(f"Valid: {len(df_clean)} kontak.")
            st.dataframe(df_clean.head())
            
            st.subheader("2. Pilih Template")
            # List template sebaiknya hardcode dulu sesuai yang sudah diapprove Meta
            template_name = st.selectbox("Template Name (Meta)", ["hello_world", "hsi_ujian_reminder", "hsi_info"])
            
            if st.button("🔥 START BLASTING"):
                # Siapkan payload
                payload = {
                    "template_name": template_name,
                    "targets": df_clean.to_dict(orient="records")
                }
                
                try:
                    with st.spinner("Menghubungi Backend..."):
                        res = requests.post(f"{BACKEND_URL}/start-blast/", json=payload)
                        if res.status_code == 200:
                            st.success(f"Job diterima! {res.json()['message']}")
                            st.info("Silakan cek tab History Log untuk memantau progress.")
                        else:
                            st.error(f"Error Backend: {res.text}")
                except Exception as e:
                    st.error(f"Gagal koneksi ke Backend: {e}")
                    st.warning("Pastikan file 'main.py' sudah dijalankan!")

        else:
            st.error(msg)

with tab2:
    st.subheader("Live Delivery Logs")
    if st.button("Refresh Logs"):
        try:
            res = requests.get(f"{BACKEND_URL}/logs/")
            data = res.json()
            if data:
                df_logs = pd.DataFrame(data)
                st.dataframe(df_logs)
            else:
                st.info("Belum ada log.")
        except:
            st.error("Tidak bisa konek ke backend.")