from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import time
from functools import lru_cache

app = Flask(__name__)

# Configuration
API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY"  # Users need to get free API key
BASE_URL = "https://www.alphavantage.co/query"

# Indonesian stock symbols - comprehensive list of major BEI/IDX stocks
# Organized by sectors for better maintainability
BEI_STOCKS = [
    # === BANKING SECTOR ===
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BDMN.JK", 
    "BTPS.JK", "MEGA.JK", "BRIS.JK", "NISP.JK", "PNBN.JK",
    "MAYA.JK", "AGRO.JK", "BABP.JK", "BINA.JK", "BNBA.JK",
    
    # === MINING & ENERGY ===
    "ANTM.JK", "TINS.JK", "INCO.JK", "PTBA.JK", "ADRO.JK", 
    "ITMG.JK", "BUMI.JK", "HRUM.JK", "GEMS.JK", "DEWA.JK",
    "PGAS.JK", "AKRA.JK", "MEDC.JK", "ELSA.JK", "ENRG.JK",
    
    # === CONSUMER GOODS ===
    "UNVR.JK", "INDF.JK", "ICBP.JK", "KLBF.JK", "KAEF.JK", 
    "MYOR.JK", "SIDO.JK", "TCID.JK", "DLTA.JK", "MLBI.JK",
    "HMSP.JK", "GGRM.JK", "RMBA.JK", "WIIM.JK", "ULTJ.JK",
    "GOOD.JK", "KINO.JK", "MBTO.JK", "PSDN.JK", "SKBM.JK",
    
    # === TELECOMMUNICATIONS & TECHNOLOGY ===
    "TLKM.JK", "EXCL.JK", "ISAT.JK", "FREN.JK", "BTEL.JK",
    "LINK.JK", "KBLV.JK", "WIFI.JK", "DNET.JK", "CENT.JK",
    
    # === AUTOMOTIVE & TRANSPORTATION ===
    "ASII.JK", "UNTR.JK", "AUTO.JK", "IMAS.JK", "INDS.JK",
    "SMSM.JK", "GJTL.JK", "NIPS.JK", "LPIN.JK", "TAXI.JK",
    "WEHA.JK", "TRIM.JK", "GDYR.JK", "BOLT.JK", "TRAM.JK",
    
    # === PROPERTY & CONSTRUCTION ===
    "BSDE.JK", "LPKR.JK", "WSKT.JK", "ADHI.JK", "WIKA.JK",
    "PTPP.JK", "SMRA.JK", "APLN.JK", "ASRI.JK", "CTRA.JK",
    "DILD.JK", "EMDE.JK", "JRPT.JK", "KIJA.JK", "PWON.JK",
    "TOTL.JK", "BEST.JK", "COWL.JK", "DART.JK", "GPRA.JK",
    
    # === RETAIL & TRADE ===
    "MAPI.JK", "ACES.JK", "HERO.JK", "RALS.JK", "AMRT.JK",
    "CSAP.JK", "ERAA.JK", "LPPF.JK", "MIDI.JK", "RANC.JK",
    
    # === MANUFACTURING & INDUSTRIALS ===
    "SMGR.JK", "INTP.JK", "SEMEN.JK", "WTON.JK", "ARNA.JK",
    "STEEL.JK", "JPFA.JK", "MAIN.JK", "TPIA.JK", "TKIM.JK",
    "SRIL.JK", "LION.JK", "YELO.JK", "ZINC.JK", "ALKA.JK",
    
    # === HEALTHCARE & PHARMACEUTICALS ===
    "HEAL.JK", "SILO.JK", "MERK.JK", "PYFA.JK", "PRDA.JK",
    "DVLA.JK", "INAF.JK", "TSPC.JK", "MTDL.JK", "SAME.JK",
    
    # === AGRICULTURE & PLANTATION ===
    "AALI.JK", "LSIP.JK", "SIMP.JK", "UNSP.JK", "TBLA.JK",
    "SGRO.JK", "ANJT.JK", "DSNG.JK", "PALM.JK", "SMAR.JK",
    
    # === FINANCIAL SERVICES ===
    "BBKP.JK", "BFIN.JK", "LPGI.JK", "MFIN.JK", "ADMF.JK",
    "APIC.JK", "AHAP.JK", "AMAG.JK", "ASDM.JK", "CFIN.JK",
    
    # === MEDIA & ADVERTISING ===
    "EMTK.JK", "SCMA.JK", "VIVA.JK", "FILM.JK", "BLTZ.JK",
    
    # === UTILITIES ===
    "RAJA.JK", "PJAA.JK", "WINS.JK",
    
    # === INVESTMENT & HOLDING COMPANIES ===
    "BMTR.JK", "BRAM.JK", "CPIN.JK", "JPRS.JK", "MTLA.JK",
    "TOWR.JK", "IPCM.JK", "PANI.JK"
]

STOCK_NAMES = {
    # === BANKING SECTOR ===
    "BBCA.JK": "Bank Central Asia Tbk",
    "BBRI.JK": "Bank Rakyat Indonesia Tbk",
    "BMRI.JK": "Bank Mandiri Tbk",
    "BBNI.JK": "Bank Negara Indonesia Tbk",
    "BDMN.JK": "Bank Danamon Indonesia Tbk",
    "BTPS.JK": "Bank BTPN Syariah Tbk",
    "MEGA.JK": "Bank Mega Tbk",
    "BRIS.JK": "Bank BRI Syariah Tbk",
    "NISP.JK": "Bank OCBC NISP Tbk",
    "PNBN.JK": "Bank Pan Indonesia Tbk",
    "MAYA.JK": "Bank Mayapada Internasional Tbk",
    "AGRO.JK": "Bank Rakyat Indonesia Agroniaga Tbk",
    "BABP.JK": "Bank ICB Bumiputera Tbk",
    "BINA.JK": "Bank Bina Artha Tbk",
    "BNBA.JK": "Bank Bumi Arta Tbk",
    
    # === MINING & ENERGY ===
    "ANTM.JK": "Aneka Tambang Tbk",
    "TINS.JK": "Timah Tbk",
    "INCO.JK": "Vale Indonesia Tbk",
    "PTBA.JK": "Bukit Asam Tbk",
    "ADRO.JK": "Adaro Energy Tbk",
    "ITMG.JK": "Indo Tambangraya Megah Tbk",
    "BUMI.JK": "Bumi Resources Tbk",
    "HRUM.JK": "Harum Energy Tbk",
    "GEMS.JK": "Golden Energy Mines Tbk",
    "DEWA.JK": "Darma Henwa Tbk",
    "PGAS.JK": "Perusahaan Gas Negara Tbk",
    "AKRA.JK": "AKR Corporindo Tbk",
    "MEDC.JK": "Medco Energi Internasional Tbk",
    "ELSA.JK": "Elnusa Tbk",
    "ENRG.JK": "Energi Mega Persada Tbk",
    
    # === CONSUMER GOODS ===
    "UNVR.JK": "Unilever Indonesia Tbk",
    "INDF.JK": "Indofood Sukses Makmur Tbk",
    "ICBP.JK": "Indofood CBP Sukses Makmur Tbk",
    "KLBF.JK": "Kalbe Farma Tbk",
    "KAEF.JK": "Kimia Farma Tbk",
    "MYOR.JK": "Mayora Indah Tbk",
    "SIDO.JK": "Industri Jamu dan Farmasi Sido Muncul Tbk",
    "TCID.JK": "Mandom Indonesia Tbk",
    "DLTA.JK": "Delta Djakarta Tbk",
    "MLBI.JK": "Multi Bintang Indonesia Tbk",
    "HMSP.JK": "HM Sampoerna Tbk",
    "GGRM.JK": "Gudang Garam Tbk",
    "RMBA.JK": "Bentoel Internasional Investama Tbk",
    "WIIM.JK": "Wismilak Inti Makmur Tbk",
    "ULTJ.JK": "Ultra Jaya Milk Industry Tbk",
    "GOOD.JK": "Garudafood Putra Putri Jaya Tbk",
    "KINO.JK": "Kino Indonesia Tbk",
    "MBTO.JK": "Martina Berto Tbk",
    "PSDN.JK": "Prasidha Aneka Niaga Tbk",
    "SKBM.JK": "Sekar Bumi Tbk",
    
    # === TELECOMMUNICATIONS & TECHNOLOGY ===
    "TLKM.JK": "Telkom Indonesia Tbk",
    "EXCL.JK": "XL Axiata Tbk",
    "ISAT.JK": "Indosat Ooredoo Hutchison Tbk",
    "FREN.JK": "Smartfren Telecom Tbk",
    "BTEL.JK": "Bakrie Telecom Tbk",
    "LINK.JK": "Link Net Tbk",
    "KBLV.JK": "First Media Tbk",
    "WIFI.JK": "Solusi Bangun Indonesia Tbk",
    "DNET.JK": "Dyviacom Intrabumi Tbk",
    "CENT.JK": "Centratama Telekomunikasi Indonesia Tbk",
    
    # === AUTOMOTIVE & TRANSPORTATION ===
    "ASII.JK": "Astra International Tbk",
    "UNTR.JK": "United Tractors Tbk",
    "AUTO.JK": "Astra Otoparts Tbk",
    "IMAS.JK": "Indomobil Sukses Internasional Tbk",
    "INDS.JK": "Indospring Tbk",
    "SMSM.JK": "Selamat Sempurna Tbk",
    "GJTL.JK": "Gajah Tunggal Tbk",
    "NIPS.JK": "Nipress Tbk",
    "LPIN.JK": "Multi Prima Sejahtera Tbk",
    "TAXI.JK": "Express Transindo Utama Tbk",
    "WEHA.JK": "Panorama Transportasi Tbk",
    "TRIM.JK": "Trimarc Investama Utama Tbk",
    "GDYR.JK": "Goodyear Indonesia Tbk",
    "BOLT.JK": "Garuda Metalindo Tbk",
    "TRAM.JK": "Trada Maritime Tbk",
    
    # === PROPERTY & CONSTRUCTION ===
    "BSDE.JK": "Bumi Serpong Damai Tbk",
    "LPKR.JK": "Lippo Karawaci Tbk",
    "WSKT.JK": "Waskita Karya Tbk",
    "ADHI.JK": "Adhi Karya Tbk",
    "WIKA.JK": "Wijaya Karya Tbk",
    "PTPP.JK": "PP Tbk",
    "SMRA.JK": "Summarecon Agung Tbk",
    "APLN.JK": "Agung Podomoro Land Tbk",
    "ASRI.JK": "Alam Sutera Realty Tbk",
    "CTRA.JK": "Ciputra Development Tbk",
    "DILD.JK": "Intiland Development Tbk",
    "EMDE.JK": "Megapolitan Developments Tbk",
    "JRPT.JK": "Jaya Real Property Tbk",
    "KIJA.JK": "Kawasan Industri Jababeka Tbk",
    "PWON.JK": "Pakuwon Jati Tbk",
    "TOTL.JK": "Total Bangun Persada Tbk",
    "BEST.JK": "Bekasi Fajar Industrial Estate Tbk",
    "COWL.JK": "Cowell Development Tbk",
    "DART.JK": "Duta Anggada Realty Tbk",
    "GPRA.JK": "Perdana Gapuraprima Tbk",
    
    # === RETAIL & TRADE ===
    "MAPI.JK": "Mitra Adiperkasa Tbk",
    "ACES.JK": "Ace Hardware Indonesia Tbk",
    "HERO.JK": "Hero Supermarket Tbk",
    "RALS.JK": "Ramayana Lestari Sentosa Tbk",
    "AMRT.JK": "Sumber Alfaria Trijaya Tbk",
    "CSAP.JK": "Catur Sentosa Adiprana Tbk",
    "ERAA.JK": "Erajaya Swasembada Tbk",
    "LPPF.JK": "Matahari Department Store Tbk",
    "MIDI.JK": "Midi Utama Indonesia Tbk",
    "RANC.JK": "Supra Boga Lestari Tbk",
    
    # === MANUFACTURING & INDUSTRIALS ===
    "SMGR.JK": "Semen Indonesia Tbk",
    "INTP.JK": "Indocement Tunggal Prakarsa Tbk",
    "SEMEN.JK": "Semen Baturaja Tbk",
    "WTON.JK": "Wijaya Karya Beton Tbk",
    "ARNA.JK": "Arwana Citramulia Tbk",
    "STEEL.JK": "Krakatau Steel Tbk",
    "JPFA.JK": "Japfa Comfeed Indonesia Tbk",
    "MAIN.JK": "Malindo Feedmill Tbk",
    "TPIA.JK": "Chandra Asri Petrochemical Tbk",
    "TKIM.JK": "Pabrik Kertas Tjiwi Kimia Tbk",
    "SRIL.JK": "Sri Rejeki Isman Tbk",
    "LION.JK": "Lion Metal Works Tbk",
    "YELO.JK": "Yelooo Integra Datanet Tbk",
    "ZINC.JK": "Kapuas Prima Coal Tbk",
    "ALKA.JK": "Alaska Industrindo Tbk",
    
    # === HEALTHCARE & PHARMACEUTICALS ===
    "HEAL.JK": "Medikaloka Hermina Tbk",
    "SILO.JK": "Siloam International Hospitals Tbk",
    "MERK.JK": "Merck Tbk",
    "PYFA.JK": "Pyridam Farma Tbk",
    "PRDA.JK": "Perdana Karya Perkasa Tbk",
    "DVLA.JK": "Darya-Varia Laboratoria Tbk",
    "INAF.JK": "Indofarma Tbk",
    "TSPC.JK": "Tempo Scan Pacific Tbk",
    "MTDL.JK": "Metrodata Electronics Tbk",
    "SAME.JK": "Sarana Meditama Metropolitan Tbk",
    
    # === AGRICULTURE & PLANTATION ===
    "AALI.JK": "Astra Agro Lestari Tbk",
    "LSIP.JK": "PP London Sumatra Indonesia Tbk",
    "SIMP.JK": "Salim Ivomas Pratama Tbk",
    "UNSP.JK": "Bakrie Sumatera Plantations Tbk",
    "TBLA.JK": "Tunas Baru Lampung Tbk",
    "SGRO.JK": "Sampoerna Agro Tbk",
    "ANJT.JK": "Austindo Nusantara Jaya Tbk",
    "DSNG.JK": "Dharma Satya Nusantara Tbk",
    "PALM.JK": "Provident Agro Tbk",
    "SMAR.JK": "Sinar Mas Agro Resources and Technology Tbk",
    
    # === FINANCIAL SERVICES ===
    "BBKP.JK": "Bank Bukopin Tbk",
    "BFIN.JK": "BFI Finance Indonesia Tbk",
    "LPGI.JK": "Lippo General Insurance Tbk",
    "MFIN.JK": "Mandala Multifinance Tbk",
    "ADMF.JK": "Adira Dinamika Multi Finance Tbk",
    "APIC.JK": "Asuransi Bina Dana Arta Tbk",
    "AHAP.JK": "Asuransi Harta Aman Pratama Tbk",
    "AMAG.JK": "Asuransi Multi Artha Guna Tbk",
    "ASDM.JK": "Asuransi Dayin Mitra Tbk",
    "CFIN.JK": "Clipan Finance Indonesia Tbk",
    
    # === MEDIA & ADVERTISING ===
    "EMTK.JK": "Elang Mahkota Teknologi Tbk",
    "SCMA.JK": "Surya Citra Media Tbk",
    "VIVA.JK": "Visi Media Asia Tbk",
    "FILM.JK": "MD Pictures Tbk",
    "BLTZ.JK": "Blitz Megaplex Tbk",
    
    # === UTILITIES ===
    "RAJA.JK": "Rukun Raharja Tbk",
    "PJAA.JK": "Pembangunan Jaya Ancol Tbk",
    "WINS.JK": "Wintermar Offshore Marine Tbk",
    
    # === INVESTMENT & HOLDING COMPANIES ===
    "BMTR.JK": "Global Mediacom Tbk",
    "BRAM.JK": "Indo Kordsa Tbk",
    "CPIN.JK": "Charoen Pokphand Indonesia Tbk",
    "JPRS.JK": "Jaya Pari Steel Tbk",
    "MTLA.JK": "Metroland Tbk",
    "TOWR.JK": "Sarana Menara Nusantara Tbk",
    "IPCM.JK": "Sat Nusapersada Tbk",
    "PANI.JK": "Pratama Abadi Nusa Industri Tbk"
}

@lru_cache(maxsize=100)
def get_stock_data(symbol, api_key=None):
    """Get stock data from Alpha Vantage API with caching"""
    if not api_key:
        # Fallback to Yahoo Finance scraping for demo
        return get_yahoo_finance_data(symbol)
    
    try:
        url = f"{BASE_URL}?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if "Time Series (Daily)" in data:
            time_series = data["Time Series (Daily)"]
            dates = sorted(time_series.keys(), reverse=True)
            
            if len(dates) >= 2:
                today = dates[0]
                yesterday = dates[1]
                
                today_data = time_series[today]
                yesterday_data = time_series[yesterday]
                
                return {
                    "symbol": symbol,
                    "today_open": float(today_data["1. open"]),
                    "today_close": float(today_data["4. close"]),
                    "yesterday_close": float(yesterday_data["4. close"]),
                    "volume": int(today_data["5. volume"]),
                    "price": float(today_data["4. close"])
                }
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def get_yahoo_finance_data(symbol):
    """Fallback function to simulate stock data"""
    # This is a simulation - in real implementation, you'd scrape Yahoo Finance
    # or use another free API
    import random
    
    base_price = random.uniform(1000, 10000)
    return {
        "symbol": symbol,
        "today_open": round(base_price * random.uniform(0.98, 1.02), 2),
        "today_close": round(base_price, 2),
        "yesterday_close": round(base_price * random.uniform(0.98, 1.02), 2),
        "volume": random.randint(1000000, 100000000),
        "price": round(base_price, 2)
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/screener')
def screener():
    return render_template('screener.html')

@app.route('/broker-analysis')
def broker_analysis():
    return render_template('broker_analysis.html')

@app.route('/foreign-flow')
def foreign_flow():
    return render_template('foreign_flow.html')

@app.route('/api/screen-open-close')
def screen_open_close():
    """Find stocks where today's open equals yesterday's close"""
    results = []
    
    for symbol in BEI_STOCKS:
        data = get_stock_data(symbol)
        if data:
            # Check if today's open equals yesterday's close (with small tolerance)
            if abs(data["today_open"] - data["yesterday_close"]) < 0.01:
                results.append({
                    "symbol": symbol.replace(".JK", ""),
                    "name": STOCK_NAMES.get(symbol, "Unknown"),
                    "price": data["price"],
                    "volume": data["volume"],
                    "today_open": data["today_open"],
                    "yesterday_close": data["yesterday_close"]
                })
        
        # Rate limiting
        time.sleep(0.1)
    
    return jsonify(results)

@app.route('/api/broker-summary/<symbol>')
def broker_summary(symbol):
    """Get broker summary for a specific stock"""
    # This is simulated data - in real implementation, you'd get this from IDX or broker API
    import random
    
    brokers = ["UBS", "Goldman Sachs", "Morgan Stanley", "Mandiri Sekuritas", "BCA Sekuritas"]
    
    top_buyers = []
    top_sellers = []
    
    for i in range(5):
        top_buyers.append({
            "broker": random.choice(brokers),
            "net_buy": random.randint(1000000, 50000000)
        })
        
        top_sellers.append({
            "broker": random.choice(brokers),
            "net_sell": random.randint(1000000, 50000000)
        })
    
    return jsonify({
        "symbol": symbol,
        "top_buyers": sorted(top_buyers, key=lambda x: x["net_buy"], reverse=True),
        "top_sellers": sorted(top_sellers, key=lambda x: x["net_sell"], reverse=True)
    })

@app.route('/api/foreign-flow/<symbol>')
def foreign_flow_data(symbol):
    """Get foreign flow data for a specific stock"""
    import random
    
    foreign_buy = random.randint(5000000, 100000000)
    foreign_sell = random.randint(5000000, 100000000)
    net_flow = foreign_buy - foreign_sell
    
    return jsonify({
        "symbol": symbol,
        "foreign_buy": foreign_buy,
        "foreign_sell": foreign_sell,
        "net_flow": net_flow
    })

if __name__ == '__main__':
    print("🚀 Starting BEI Stock Screener...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("📊 Happy trading!")
    app.run(debug=True, host='0.0.0.0', port=5000)