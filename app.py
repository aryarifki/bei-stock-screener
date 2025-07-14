from flask import Flask, render_template, request, jsonify
import requests
import polars as pl
from datetime import datetime, timedelta
import json
import time
from functools import lru_cache

app = Flask(__name__)

# Configuration
API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY"  # Users need to get free API key
BASE_URL = "https://www.alphavantage.co/query"

# Indonesian stock symbols - comprehensive list of 150+ major stocks
# Organized by sectors for better maintainability and coverage of liquid stocks from IDX30, LQ45, and IDX80
BEI_STOCKS = [
    # Banking Sector
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BDMN.JK", "BTPS.JK",
    "MEGA.JK", "BRIS.JK", "BJBR.JK", "BACA.JK", "MAYA.JK", "NISP.JK",
    "BNGA.JK", "BNBA.JK", "PNBN.JK", "AGRO.JK", "BBYB.JK", "MCOR.JK",
    
    # Mining & Natural Resources
    "ANTM.JK", "TINS.JK", "INCO.JK", "PTBA.JK", "ADRO.JK", "ITMG.JK",
    "BUMI.JK", "HRUM.JK", "KKGI.JK", "PTRO.JK", "DEWA.JK", "GEMS.JK",
    "BYAN.JK", "MYOH.JK", "FIRE.JK", "TOBA.JK", "BORN.JK", "SMMT.JK",
    
    # Consumer Goods & Food
    "UNVR.JK", "INDF.JK", "ICBP.JK", "KLBF.JK", "KAEF.JK", "MYOR.JK",
    "SIDO.JK", "TCID.JK", "CEKA.JK", "DLTA.JK", "MLBI.JK", "CAMP.JK",
    "HMSP.JK", "GGRM.JK", "RMBA.JK", "WIIM.JK", "DVLA.JK", "MBTO.JK",
    
    # Technology & Telecommunications
    "TLKM.JK", "EXCL.JK", "ISAT.JK", "FREN.JK", "BTEL.JK", "KBLV.JK",
    "MTEL.JK", "DNET.JK", "LINK.JK", "KIOS.JK", "MICE.JK", "ZBRA.JK",
    
    # Automotive & Heavy Equipment
    "ASII.JK", "UNTR.JK", "AUTO.JK", "IMAS.JK", "INDS.JK", "NIPS.JK",
    "GDYR.JK", "GJTL.JK", "SMSM.JK", "LPIN.JK", "MASA.JK", "BOLT.JK",
    
    # Property & Construction
    "BSDE.JK", "LPKR.JK", "WSKT.JK", "ADHI.JK", "WIKA.JK", "PTPP.JK",
    "PWON.JK", "SMRA.JK", "CTRA.JK", "ASRI.JK", "BKSL.JK", "COWL.JK",
    "DILD.JK", "JRPT.JK", "KIJA.JK", "MDLN.JK", "APLN.JK", "TOTL.JK",
    
    # Energy & Utilities
    "PGAS.JK", "AKRA.JK", "MEDC.JK", "ELSA.JK", "ENRG.JK", "APEX.JK",
    "RAJA.JK", "RUIS.JK", "SURE.JK", "ARTI.JK", "BIPI.JK", "CNKO.JK",
    
    # Retail & Services
    "MAPI.JK", "ACES.JK", "HERO.JK", "RALS.JK", "LPPF.JK", "AMRT.JK",
    "ERAA.JK", "CSAP.JK", "SILO.JK", "TRIO.JK", "GOLD.JK", "PANR.JK",
    
    # Transportation & Logistics
    "JSMR.JK", "GIAA.JK", "BIRD.JK", "WEHA.JK", "SMDR.JK", "TRAM.JK",
    "AKSI.JK", "CMPP.JK", "NELY.JK", "SAFE.JK", "SHIP.JK", "TAXI.JK",
    
    # Manufacturing & Industrial
    "SMGR.JK", "INTP.JK", "WTON.JK", "SEMEN.JK", "TPIA.JK", "ALKA.JK",
    "FPNI.JK", "LION.JK", "JKON.JK", "PICO.JK", "STAR.JK", "STEEL.JK",
    
    # Plantation & Agriculture
    "AALI.JK", "SIMP.JK", "LSIP.JK", "UNSP.JK", "TBLA.JK", "SSMS.JK",
    "SMAR.JK", "GOLL.JK", "PALM.JK", "ANJT.JK", "BWPT.JK", "DSNG.JK",
    
    # Media & Entertainment
    "SCMA.JK", "VIVA.JK", "EMTK.JK", "JAWA.JK", "LAPD.JK", "MGNA.JK",
    
    # Healthcare & Pharmaceuticals
    "HEAL.JK", "PRDA.JK", "MERK.JK", "PYFA.JK", "TSPC.JK", "WOOD.JK",
    
    # Financial Services (Non-Banking)
    "AHAP.JK", "BBLD.JK", "BFIN.JK", "WOMF.JK", "ADMF.JK", "CFIN.JK",
    
    # Additional Blue-Chip & Liquid Stocks from IDX30/LQ45/IDX80
    "INKP.JK", "TOWR.JK", "BRPT.JK", "JPFA.JK", "CPIN.JK", "TBIG.JK"
]

STOCK_NAMES = {
    # Banking Sector
    "BBCA.JK": "Bank Central Asia Tbk",
    "BBRI.JK": "Bank Rakyat Indonesia Tbk",
    "BMRI.JK": "Bank Mandiri Tbk",
    "BBNI.JK": "Bank Negara Indonesia Tbk",
    "BDMN.JK": "Bank Danamon Indonesia Tbk",
    "BTPS.JK": "Bank BTPN Syariah Tbk",
    "MEGA.JK": "Bank Mega Tbk",
    "BRIS.JK": "Bank BRI Syariah Tbk",
    "BJBR.JK": "Bank Pembangunan Daerah Jawa Barat Banten Tbk",
    "BACA.JK": "Bank Capital Indonesia Tbk",
    "MAYA.JK": "Bank Mayapada Internasional Tbk",
    "NISP.JK": "Bank OCBC NISP Tbk",
    "BNGA.JK": "Bank CIMB Niaga Tbk",
    "BNBA.JK": "Bank Bumi Arta Tbk",
    "PNBN.JK": "Bank Pan Indonesia Tbk",
    "AGRO.JK": "Bank Rakyat Indonesia Agroniaga Tbk",
    "BBYB.JK": "Bank Yudha Bhakti Tbk",
    "MCOR.JK": "Bank China Construction Bank Indonesia Tbk",
    
    # Mining & Natural Resources
    "ANTM.JK": "Aneka Tambang Tbk",
    "TINS.JK": "Timah Tbk",
    "INCO.JK": "Vale Indonesia Tbk",
    "PTBA.JK": "Bukit Asam Tbk",
    "ADRO.JK": "Adaro Energy Tbk",
    "ITMG.JK": "Indo Tambangraya Megah Tbk",
    "BUMI.JK": "Bumi Resources Tbk",
    "HRUM.JK": "Harum Energy Tbk",
    "KKGI.JK": "Resource Alam Indonesia Tbk",
    "PTRO.JK": "Petrosea Tbk",
    "DEWA.JK": "Darma Henwa Tbk",
    "GEMS.JK": "Golden Energy Mines Tbk",
    "BYAN.JK": "Bayan Resources Tbk",
    "MYOH.JK": "Samindo Resources Tbk",
    "FIRE.JK": "Alfa Energi Investama Tbk",
    "TOBA.JK": "Toba Pulp Lestari Tbk",
    "BORN.JK": "Borneo Lumbung Energi & Metal Tbk",
    "SMMT.JK": "Golden Eagle Energy Tbk",
    
    # Consumer Goods & Food
    "UNVR.JK": "Unilever Indonesia Tbk",
    "INDF.JK": "Indofood Sukses Makmur Tbk",
    "ICBP.JK": "Indofood CBP Sukses Makmur Tbk",
    "KLBF.JK": "Kalbe Farma Tbk",
    "KAEF.JK": "Kimia Farma Tbk",
    "MYOR.JK": "Mayora Indah Tbk",
    "SIDO.JK": "Industri Jamu Dan Farmasi Sido Muncul Tbk",
    "TCID.JK": "Mandom Indonesia Tbk",
    "CEKA.JK": "Wilmar Cahaya Indonesia Tbk",
    "DLTA.JK": "Delta Djakarta Tbk",
    "MLBI.JK": "Multi Bintang Indonesia Tbk",
    "CAMP.JK": "Campina Ice Cream Industry Tbk",
    "HMSP.JK": "HM Sampoerna Tbk",
    "GGRM.JK": "Gudang Garam Tbk",
    "RMBA.JK": "Bentoel Internasional Investama Tbk",
    "WIIM.JK": "Wismilak Inti Makmur Tbk",
    "DVLA.JK": "Darya-Varia Laboratoria Tbk",
    "MBTO.JK": "Martina Berto Tbk",
    
    # Technology & Telecommunications
    "TLKM.JK": "Telkom Indonesia Tbk",
    "EXCL.JK": "XL Axiata Tbk",
    "ISAT.JK": "Indosat Ooredoo Hutchison Tbk",
    "FREN.JK": "Smartfren Telecom Tbk",
    "BTEL.JK": "Bakrie Telecom Tbk",
    "KBLV.JK": "First Media Tbk",
    "MTEL.JK": "Metrodata Electronics Tbk",
    "DNET.JK": "Dyviacom Intrabumi Tbk",
    "LINK.JK": "Link Net Tbk",
    "KIOS.JK": "Kioson Komersial Indonesia Tbk",
    "MICE.JK": "Multi Indocitra Tbk",
    "ZBRA.JK": "Zebra Nusantara Tbk",
    
    # Automotive & Heavy Equipment
    "ASII.JK": "Astra International Tbk",
    "UNTR.JK": "United Tractors Tbk",
    "AUTO.JK": "Astra Otoparts Tbk",
    "IMAS.JK": "Indomobil Sukses Internasional Tbk",
    "INDS.JK": "Indospring Tbk",
    "NIPS.JK": "Nipress Tbk",
    "GDYR.JK": "Goodyear Indonesia Tbk",
    "GJTL.JK": "Gajah Tunggal Tbk",
    "SMSM.JK": "Selamat Sempurna Tbk",
    "LPIN.JK": "Multi Prima Sejahtera Tbk",
    "MASA.JK": "Multistrada Arah Sarana Tbk",
    "BOLT.JK": "Garuda Metalindo Tbk",
    
    # Property & Construction
    "BSDE.JK": "Bumi Serpong Damai Tbk",
    "LPKR.JK": "Lippo Karawaci Tbk",
    "WSKT.JK": "Waskita Karya Tbk",
    "ADHI.JK": "Adhi Karya Tbk",
    "WIKA.JK": "Wijaya Karya Tbk",
    "PTPP.JK": "PP Tbk",
    "PWON.JK": "Pakuwon Jati Tbk",
    "SMRA.JK": "Summarecon Agung Tbk",
    "CTRA.JK": "Ciputra Development Tbk",
    "ASRI.JK": "Alam Sutera Realty Tbk",
    "BKSL.JK": "Sentul City Tbk",
    "COWL.JK": "Cowell Development Tbk",
    "DILD.JK": "Intiland Development Tbk",
    "JRPT.JK": "Jaya Real Property Tbk",
    "KIJA.JK": "Kawasan Industri Jababeka Tbk",
    "MDLN.JK": "Modernland Realty Tbk",
    "APLN.JK": "Agung Podomoro Land Tbk",
    "TOTL.JK": "Total Bangun Persada Tbk",
    
    # Energy & Utilities
    "PGAS.JK": "Perusahaan Gas Negara Tbk",
    "AKRA.JK": "AKR Corporindo Tbk",
    "MEDC.JK": "Medco Energi Internasional Tbk",
    "ELSA.JK": "Elnusa Tbk",
    "ENRG.JK": "Energi Mega Persada Tbk",
    "APEX.JK": "Apexindo Pratama Duta Tbk",
    "RAJA.JK": "Rukun Raharja Tbk",
    "RUIS.JK": "Radiant Utama Interinsco Tbk",
    "SURE.JK": "Super Energy Tbk",
    "ARTI.JK": "Ratu Prabu Energi Tbk",
    "BIPI.JK": "Astrindo Nusantara Infrastruktur Tbk",
    "CNKO.JK": "Exploitasi Energi Indonesia Tbk",
    
    # Retail & Services
    "MAPI.JK": "Mitra Adiperkasa Tbk",
    "ACES.JK": "Ace Hardware Indonesia Tbk",
    "HERO.JK": "Hero Supermarket Tbk",
    "RALS.JK": "Ramayana Lestari Sentosa Tbk",
    "LPPF.JK": "Matahari Department Store Tbk",
    "AMRT.JK": "Sumber Alfaria Trijaya Tbk",
    "ERAA.JK": "Erajaya Swasembada Tbk",
    "CSAP.JK": "Catur Sentosa Adiprana Tbk",
    "SILO.JK": "Siloam International Hospitals Tbk",
    "TRIO.JK": "Trikomsel Oke Tbk",
    "GOLD.JK": "Golden Retailindo Tbk",
    "PANR.JK": "Panorama Sentrawisata Tbk",
    
    # Transportation & Logistics
    "JSMR.JK": "Jasa Marga Tbk",
    "GIAA.JK": "Garuda Indonesia Tbk",
    "BIRD.JK": "Blue Bird Tbk",
    "WEHA.JK": "Panorama Transportasi Tbk",
    "SMDR.JK": "Samudera Indonesia Tbk",
    "TRAM.JK": "Trada Maritime Tbk",
    "AKSI.JK": "Majapahit Solusi Bersama Tbk",
    "CMPP.JK": "Centratama Menara Persada Tbk",
    "NELY.JK": "Pelayaran Nelly Dwi Putri Tbk",
    "SAFE.JK": "Steady Safe Tbk",
    "SHIP.JK": "Salam Pacific Indonesia Lines Tbk",
    "TAXI.JK": "Express Transindo Utama Tbk",
    
    # Manufacturing & Industrial
    "SMGR.JK": "Semen Indonesia Tbk",
    "INTP.JK": "Indocement Tunggal Prakarsa Tbk",
    "WTON.JK": "Wijaya Karya Beton Tbk",
    "SEMEN.JK": "Semen Baturaja Tbk",
    "TPIA.JK": "Chandra Asri Pacific Tbk",
    "ALKA.JK": "Alaska Industrindo Tbk",
    "FPNI.JK": "Lotte Chemical Titan Tbk",
    "LION.JK": "Lion Metal Works Tbk",
    "JKON.JK": "Jaya Konstruksi Manggala Pratama Tbk",
    "PICO.JK": "Pelangi Indah Canindo Tbk",
    "STAR.JK": "Star Petrochem Tbk",
    "STEEL.JK": "Krakatau Steel Tbk",
    
    # Plantation & Agriculture
    "AALI.JK": "Astra Agro Lestari Tbk",
    "SIMP.JK": "Salim Ivomas Pratama Tbk",
    "LSIP.JK": "PP London Sumatra Indonesia Tbk",
    "UNSP.JK": "Bakrie Sumatera Plantations Tbk",
    "TBLA.JK": "Tunas Baru Lampung Tbk",
    "SSMS.JK": "Sawit Sumbermas Sarana Tbk",
    "SMAR.JK": "Sinar Mas Agro Resources Technology Tbk",
    "GOLL.JK": "Golden Plantation Tbk",
    "PALM.JK": "Provident Agro Tbk",
    "ANJT.JK": "Austindo Nusantara Jaya Tbk",
    "BWPT.JK": "Eagle High Plantations Tbk",
    "DSNG.JK": "Dharma Satya Nusantara Tbk",
    
    # Media & Entertainment
    "SCMA.JK": "Surya Citra Media Tbk",
    "VIVA.JK": "Visi Media Asia Tbk",
    "EMTK.JK": "Elang Mahkota Teknologi Tbk",
    "JAWA.JK": "Jaya Agra Wattie Tbk",
    "LAPD.JK": "Lapindo Brantas Tbk",
    "MGNA.JK": "Magna Investama Mandiri Tbk",
    
    # Healthcare & Pharmaceuticals
    "HEAL.JK": "Medikaloka Hermina Tbk",
    "PRDA.JK": "Prodia Widyahusada Tbk",
    "MERK.JK": "Merck Tbk",
    "PYFA.JK": "Pyridam Farma Tbk",
    "TSPC.JK": "Tempo Scan Pacific Tbk",
    "WOOD.JK": "Integra Indocabinet Tbk",
    
    # Financial Services (Non-Banking)
    "AHAP.JK": "Asuransi Harta Aman Pratama Tbk",
    "BBLD.JK": "Buana Finance Tbk",
    "BFIN.JK": "BFI Finance Indonesia Tbk",
    "WOMF.JK": "Wahana Ottomitra Multiartha Tbk",
    "ADMF.JK": "Adira Dinamika Multi Finance Tbk",
    "CFIN.JK": "Clipan Finance Indonesia Tbk",
    
    # Additional Blue-Chip & Liquid Stocks
    "INKP.JK": "Indah Kiat Pulp & Paper Tbk",
    "TOWR.JK": "Sarana Menara Nusantara Tbk",
    "BRPT.JK": "Barito Pacific Tbk",
    "JPFA.JK": "Japfa Comfeed Indonesia Tbk",
    "CPIN.JK": "Charoen Pokphand Indonesia Tbk",
    "TBIG.JK": "Tower Bersama Infrastructure Tbk"
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
    # Collect all stock data first
    all_stock_data = []
    
    for symbol in BEI_STOCKS:
        data = get_stock_data(symbol)
        if data:
            all_stock_data.append({
                "symbol": symbol,
                "name": STOCK_NAMES.get(symbol, "Unknown"),
                "price": data["price"],
                "volume": data["volume"],
                "today_open": data["today_open"],
                "yesterday_close": data["yesterday_close"],
                "difference": abs(data["today_open"] - data["yesterday_close"])
            })
        
        # Rate limiting
        time.sleep(0.1)
    
    if not all_stock_data:
        return jsonify([])
    
    # Convert to Polars DataFrame for efficient filtering
    df = pl.DataFrame(all_stock_data)
    
    # Filter stocks where today's open equals yesterday's close (with small tolerance)
    filtered_df = df.filter(pl.col("difference") < 0.01)
    
    # Convert back to list of dictionaries for JSON response, clean up symbol names
    results = filtered_df.with_columns([
        pl.col("symbol").str.replace(".JK", "").alias("clean_symbol")
    ]).select([
        pl.col("clean_symbol").alias("symbol"),
        "name",
        "price", 
        "volume",
        "today_open",
        "yesterday_close"
    ]).to_dicts()
    
    return jsonify(results)

@app.route('/api/broker-summary/<symbol>')
def broker_summary(symbol):
    """Get broker summary for a specific stock"""
    # This is simulated data - in real implementation, you'd get this from IDX or broker API
    import random
    
    brokers = ["UBS", "Goldman Sachs", "Morgan Stanley", "Mandiri Sekuritas", "BCA Sekuritas"]
    
    # Generate broker data
    broker_data = []
    for i in range(10):  # Generate more data to better demonstrate polars sorting
        broker_data.append({
            "broker": random.choice(brokers),
            "net_buy": random.randint(1000000, 50000000),
            "net_sell": random.randint(1000000, 50000000)
        })
    
    # Use Polars for efficient data processing and sorting
    df = pl.DataFrame(broker_data)
    
    # Get top 5 buyers and sellers using polars
    top_buyers_df = df.sort("net_buy", descending=True).head(5)
    top_sellers_df = df.sort("net_sell", descending=True).head(5)
    
    return jsonify({
        "symbol": symbol,
        "top_buyers": top_buyers_df.select(["broker", "net_buy"]).to_dicts(),
        "top_sellers": top_sellers_df.select(["broker", "net_sell"]).to_dicts()
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