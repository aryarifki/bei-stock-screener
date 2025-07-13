# 📊 BEI Stock Screener untuk Termux

Tool analisis saham Bursa Efek Indonesia (BEI) yang berjalan di Termux Android dengan antarmuka web yang modern dan mobile-friendly.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Platform](https://img.shields.io/badge/platform-Termux%20Android-orange.svg)

## 🚀 Fitur Utama

### 📈 Stock Screener "Open = Previous Close"
- Mencari saham dimana harga pembukaan hari ini sama dengan penutupan kemarin
- Menampilkan hasil dalam tabel yang rapi dan mudah dibaca
- Filter otomatis dengan toleransi untuk akurasi data

### 🏦 Analisis Bandarmology
- Input kode saham untuk analisis broker tertentu
- Menampilkan Top Buyers dan Top Sellers
- Data Net Buy dan Net Sell per broker

### 🌍 Foreign Flow Analysis
- Monitor aliran dana investor asing
- Visualisasi data dengan bar chart sederhana
- Menampilkan Foreign Buy, Foreign Sell, dan Net Flow

## 🛠 Persyaratan Sistem

- **Android** dengan **Termux** terinstal
- **Python 3.8** atau lebih baru
- **Koneksi internet** untuk mengambil data saham
- **Browser** untuk mengakses Web UI

## 📥 Instalasi di Termux

### Langkah 1: Update Termux
```bash
pkg update && pkg upgrade
```

### Langkah 2: Install Paket yang Dibutuhkan
```bash
pkg install python git
```

### Langkah 3: Clone Repository
```bash
git clone https://github.com/aryarifki/bei-stock-screener.git
cd bei-stock-screener
```

### Langkah 4: Install Dependencies Python
```bash
pip install -r requirements.txt
```

### Langkah 5: (Opsional) Setup API Key
Untuk mendapatkan data real-time yang lebih akurat, daftarkan API key gratis:

1. **Alpha Vantage (Recommended)**:
   - Kunjungi: https://www.alphavantage.co/support/#api-key
   - Daftar gratis dan dapatkan API key
   - Edit file `app.py` dan ganti `YOUR_ALPHA_VANTAGE_API_KEY` dengan API key Anda

## 🎯 Cara Penggunaan

### 1. Menjalankan Aplikasi
```bash
python app.py
```

Anda akan melihat output seperti ini:
```
🚀 Starting BEI Stock Screener...
📱 Open your browser and go to: http://localhost:5000
📊 Happy trading!
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.xxx:5000
```

### 2. Mengakses Web UI
Buka browser di Android Anda dan kunjungi:
```
http://localhost:5000
```

### 3. Menggunakan Fitur-Fitur

#### Stock Screener
1. Klik menu "Screener"
2. Klik tombol "Jalankan Screener"
3. Tunggu proses dan lihat hasil

#### Broker Analysis
1. Klik menu "Broker"
2. Masukkan kode saham (contoh: BBCA)
3. Klik "Analisis"

#### Foreign Flow
1. Klik menu "Foreign Flow"
2. Masukkan kode saham (contoh: BBRI)
3. Klik "Analisis"

## 📊 Sumber Data

### API yang Digunakan

**Alpha Vantage (Primary)**
- **Alasan Pemilihan**: Coverage terbaik untuk saham global termasuk Indonesia
- **Keunggulan**: 
  - Data historis lengkap
  - End-of-day data akurat
  - API gratis dengan limit 5 calls/minute, 500 calls/day
  - Dokumentasi lengkap
- **Format Data**: JSON dengan struktur yang konsisten
- **Reliability**: 99.9% uptime

**Fallback Options**:
- Yahoo Finance (scraping mode untuk demo)
- Marketstack (alternatif berbayar)
- Twelve Data (alternatif dengan free tier)

### Catatan Penting
- Mode demo menggunakan data simulasi untuk testing
- Untuk trading real, pastikan menggunakan API key yang valid
- Data delay sekitar 15-20 menit (normal untuk API gratis)

## 🔧 Konfigurasi

### File Konfigurasi Utama

**app.py** - Konfigurasi server dan API:
```python
# Ganti dengan API key Anda
API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY"

# Tambah saham BEI lainnya di sini
BEI_STOCKS = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", 
    # ... tambahkan sesuai kebutuhan
]
```

### Port dan Host
Default: `localhost:5000`

Untuk mengakses dari device lain di network yang sama:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 🎨 Struktur File

```
bei-stock-screener/
├── app.py                 # Aplikasi Flask utama
├── requirements.txt       # Dependencies Python
├── README.md             # Dokumentasi ini
├── templates/            # Template HTML
│   ├── base.html         # Template dasar
│   ├── index.html        # Halaman utama
│   ├── screener.html     # Halaman screener
│   ├── broker_analysis.html
│   └── foreign_flow.html
└── static/               # File CSS dan JS
    ├── css/
    │   └── style.css     # Styling utama
    └── js/
        └── app.js        # JavaScript functions
```

## 🔍 Troubleshooting

### Error: "No module named 'flask'"
```bash
pip install flask
```

### Error: "Permission denied"
```bash
chmod +x app.py
```

### Error: "Address already in use"
```bash
# Hentikan proses yang menggunakan port 5000
pkill -f python
# Atau ganti port di app.py
```

### Tidak bisa akses dari browser
1. Pastikan Termux dan browser di device yang sama
2. Cek firewall/security settings
3. Coba akses via: `http://127.0.0.1:5000`

### Data tidak akurat
1. Daftarkan API key di Alpha Vantage
2. Pastikan koneksi internet stabil
3. Cek log error di terminal Termux

## 🎯 Tips Penggunaan

### Performa Optimal
- Gunakan WiFi untuk koneksi stabil
- Close aplikasi lain untuk menghemat RAM
- Gunakan mode landscape untuk UI lebih luas

### Keyboard Shortcuts
- **Ctrl + R**: Refresh data
- **Escape**: Clear input fields
- **Enter**: Submit form (di input fields)

### Best Practices
- Jangan refresh terlalu sering (rate limit API)
- Simpan kode saham favorit di notes
- Monitor di jam trading (09:00-16:00 WIB)

## 🛡 Keamanan

- Tool berjalan local di device Anda
- Tidak ada data yang dikirim ke server eksternal
- API key disimpan local di file konfigurasi
- Koneksi HTTP hanya untuk localhost

## 🔮 Roadmap

### Version 1.1
- [ ] Support untuk lebih banyak saham BEI
- [ ] Historical chart integration
- [ ] Notification system
- [ ] Export data ke CSV

### Version 1.2
- [ ] Technical indicators
- [ ] Portfolio tracking
- [ ] Real-time websocket data
- [ ] Dark mode

## 🤝 Kontribusi

1. Fork repository
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Buat Pull Request

## 📜 Lisensi

MIT License - Bebas digunakan untuk personal dan komersial.

## 📞 Support

Jika mengalami masalah:
1. Baca troubleshooting section
2. Check issues di GitHub
3. Buat issue baru dengan detail lengkap

---

**Happy Trading! 📈**

*Disclaimer: Tool ini untuk tujuan edukasi dan analisis. Selalu lakukan riset mendalam sebelum berinvestasi.*