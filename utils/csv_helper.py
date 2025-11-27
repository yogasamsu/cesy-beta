import pandas as pd

def clean_phone_number(phone):
    """
    Mengubah format 08xx atau 8xx menjadi 628xx.
    Menghapus karakter non-angka.
    """
    if pd.isna(phone):
        return None
    
    # Hapus spasi, strip, dll
    p = str(phone).strip().replace("-", "").replace(" ", "").replace("+", "")
    
    # Logic 62
    if p.startswith("0"):
        return "62" + p[1:]
    elif p.startswith("8"):
        return "62" + p
    
    return p

def process_csv(file):
    """
    Menerima file upload, mengembalikan DataFrame bersih.
    """
    try:
        df = pd.read_csv(file)
        
        # Validasi kolom
        required_cols = ['Name', 'Phone']
        if not all(col in df.columns for col in required_cols):
            return None, "Format CSV salah. Wajib ada kolom: 'Name' dan 'Phone'"
        
        # Bersihkan nomor
        df['Phone'] = df['Phone'].apply(clean_phone_number)
        
        # Hapus yang kosong/invalid
        df = df.dropna(subset=['Phone'])
        
        return df, "Success"
    except Exception as e:
        return None, str(e)