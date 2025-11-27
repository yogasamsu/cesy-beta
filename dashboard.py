import streamlit as st
import pandas as pd
from utils.wa_sender import send_message
import time
import random

st.set_page_config(page_title="Cesy - HSI Edu", layout="wide")

st.title("📢 Cesy: Campaign Blaster")

# 1. Upload CSV
uploaded_file = st.file_uploader("Upload CSV Peserta (Kolom: Name, Phone)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Cleaning Number Logic (Simple)
    # Pastikan tipe data string agar 0 di depan tidak hilang
    df['Phone'] = df['Phone'].astype(str)
    # Ubah 08xx jadi 628xx
    df['Phone'] = df['Phone'].apply(lambda x: '62' + x[1:] if x.startswith('0') else x)
    
    st.dataframe(df.head())
    st.info(f"Total Kontak: {len(df)} user")

    # 2. Compose Message
    st.divider()
    st.subheader("Tulis Pesan")
    st.caption("Gunakan {Name} untuk memanggil nama otomatis.")
    
    message_template = st.text_area("Isi Pesan", height=150, 
                                    value="Assalamualaikum {Name}, jangan lupa setoran hafalan ya.")
    
    # Preview
    if not df.empty:
        sample_msg = message_template.replace("{Name}", df.iloc[0]['Name'])
        st.warning(f"Preview (ke {df.iloc[0]['Phone']}):\n\n{sample_msg}")

    # 3. Action Blast
    if st.button("🚀 KIRIM BLAST SEKARANG"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        success_count = 0
        fail_count = 0
        
        for index, row in df.iterrows():
            # Update status
            status_text.text(f"Mengirim ke {row['Name']}...")
            
            # Panggil fungsi kirim
            is_sent, log = send_message(row['Phone'], row['Name'], message_template)
            
            if is_sent:
                success_count += 1
            else:
                fail_count += 1
                st.error(f"Gagal ke {row['Name']}: {log}")
            
            # Update Progress Bar
            progress_bar.progress((index + 1) / len(df))
            
            # PENTING: Jeda waktu agar tidak dianggap spammer oleh Meta
            time.sleep(random.uniform(1, 3)) 
            
        st.success(f"Selesai! Sukses: {success_count}, Gagal: {fail_count}")