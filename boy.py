import requests 
import re
import time
import random
import schedule
from datetime import datetime, timedelta
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor

# Fungsi untuk membaca data langsung dari URL
def baca_dari_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        print(f"Gagal membaca dari {url}: {e}")
        exit()

# Fungsi untuk multi request
def multi_request(urls):
    with ThreadPoolExecutor() as executor:
        responses = list(executor.map(lambda url: requests.get(url).json(), urls))
    return responses

# Fungsi utama
def tugas_utama():
    print("Memulai proses...")
    
    # URL file
    url_token = "http://jayafb.xyz/bot/fptoken.txt"
    url_status = "http://jayafb.xyz/bot/idstatus.txt"
    
    # Baca data dari URL
    token = baca_dari_url(url_token)
    konten_status = baca_dari_url(url_status)
    
    # Parsing status
    pola = r'Nama: (.*)\nStatus ID: (\d+_\d+)'
    kecocokan = re.findall(pola, konten_status)
    
    if not kecocokan:
        print("Format file status tidak valid")
        return
    
    target = "Jaya & Edah"
    url_cek = [f"https://graph.facebook.com/{id_}?fields=comments.limit(100){{from{{name}}}}&access_token={token}" 
               for _, id_ in kecocokan]
    
    responses = multi_request(url_cek)
    aksi = []
    
    # Filter status yang perlu interaksi
    for i, resp in enumerate(responses):
        if 'error' in resp:
            print(f"Error: {resp['error']['message']}")
            continue
        
        komentar = resp.get('comments', {}).get('data', [])
        ditemukan = any(k.get('from', {}).get('name') == target for k in komentar)
        
        if not ditemukan:
            aksi.append(kecocokan[i])
    
    if not aksi:
        print("Tidak ada aksi diperlukan")
        return
    
    # Daftar pesan
    pesan = [
        "Hadir\nJangan Lupa Mampir Di status aku ya {%name%}",
        "Kontennya makin hari makin quality! Aku Bangga 😎 Jangan lupa balik dukungannya di Kontenku ya!\n#salam_intraksi",
    ]
    
    # Proses interaksi
    for idx, (nama, id_) in enumerate(aksi):
        # Tentukan ucapan waktu
        waktu = datetime.utcnow() + timedelta(hours=7)
        jam = waktu.hour
        
        if 0 <= jam < 10:
            ucapan = f"Selamat Pagi {nama},"
        elif 10 <= jam < 15:
            ucapan = f"Selamat Siang {nama},"
        elif 15 <= jam < 18:
            ucapan = f"Selamat Sore {nama},"
        else:
            ucapan = f"Selamat Malam {nama},"
        
        # Pilih pesan acak
        pesan_terpilih = random.choice(pesan).replace('{%name%}', nama)
        pesan_final = quote(f"{ucapan}\n{pesan_terpilih}")
        
        # URL interaksi
        url_komentar = f"https://graph.facebook.com/{id_}/comments?message={pesan_final}&method=post&access_token={token}"
        url_reaksi = f"https://graph.facebook.com/{id_}/reactions?type={random.choice(['LIKE','LOVE','HAHA'])}&method=post&access_token={token}"
        
        # Kirim request
        try:
            requests.post(url_komentar)
            requests.post(url_reaksi)
            print(f"Berhasil interaksi di {id_}")
        except Exception as e:
            print(f"Gagal di {id_}: {str(e)}")
        
        # Jeda 15 detik antar aksi
        if idx < len(aksi)-1:
            time.sleep(15)

# Jadwalkan setiap 5 menit
schedule.every(5).minutes.do(tugas_utama)

# Jalankan segera sekali
tugas_utama()

# Loop penjadwalan
while True:
    schedule.run_pending()
    time.sleep(1)
