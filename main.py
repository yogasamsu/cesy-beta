from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List
import sqlite3
import time
import random
from datetime import datetime
from dotenv import load_dotenv
from utils.wa_sender import send_template_to_meta

# Load env
load_dotenv()

app = FastAPI(title="Cesy Backend")

# --- DATABASE SETUP (SQLite) ---
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Tabel Log Pengiriman
    c.execute('''CREATE TABLE IF NOT EXISTS blast_logs 
                 (id INTEGER PRIMARY KEY, timestamp TEXT, phone TEXT, name TEXT, status TEXT, response TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- MODELS ---
class BlastTarget(BaseModel):
    name: str
    phone: str

class BlastRequest(BaseModel):
    template_name: str
    targets: List[BlastTarget]

# --- WORKER FUNCTION ---
def process_blast_queue(template_name: str, targets: List[BlastTarget]):
    """
    Fungsi ini berjalan di background, tidak memblokir UI.
    """
    print(f"🚀 Memulai blast ke {len(targets)} nomor...")
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    for target in targets:
        # 1. Kirim WA
        # Asumsi template punya 1 variabel {{1}} yaitu Nama
        is_sent, resp = send_template_to_meta(target.phone, template_name, [target.name])
        
        status = "SUCCESS" if is_sent else "FAILED"
        log_resp = str(resp)[:500] # Simpan log pendek aja
        
        # 2. Simpan ke DB
        c.execute("INSERT INTO blast_logs (timestamp, phone, name, status, response) VALUES (?, ?, ?, ?, ?)",
                  (datetime.now(), target.phone, target.name, status, log_resp))
        conn.commit()
        
        # 3. Random Delay (Safety)
        time.sleep(random.uniform(2.0, 5.0))
        
    conn.close()
    print("✅ Blast selesai.")

# --- ENDPOINTS ---
@app.post("/start-blast/")
async def start_blast(request: BlastRequest, background_tasks: BackgroundTasks):
    # Lempar ke background worker
    background_tasks.add_task(process_blast_queue, request.template_name, request.targets)
    return {"message": "Blast dimulai di background", "count": len(request.targets)}

@app.get("/logs/")
def get_logs():
    conn = sqlite3.connect('database.db')
    df_logs = pd.read_sql_query("SELECT * FROM blast_logs ORDER BY id DESC LIMIT 100", conn)
    conn.close()
    return df_logs.to_dict(orient="records")