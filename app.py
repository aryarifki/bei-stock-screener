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

# Indonesian stock symbols - sample list (can be expanded)
BEI_STOCKS = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", 
    "UNVR.JK", "ICBP.JK", "INDF.JK", "KLBF.JK", "HMSP.JK",
    "GGRM.JK", "SMGR.JK", "UNTR.JK", "EXCL.JK", "PGAS.JK"
]

STOCK_NAMES = {
    "BBCA.JK": "Bank Central Asia Tbk",
    "BBRI.JK": "Bank Rakyat Indonesia Tbk",
    "BMRI.JK": "Bank Mandiri Tbk",
    "TLKM.JK": "Telkom Indonesia Tbk",
    "ASII.JK": "Astra International Tbk",
    "UNVR.JK": "Unilever Indonesia Tbk",
    "ICBP.JK": "Indofood CBP Sukses Makmur Tbk",
    "INDF.JK": "Indofood Sukses Makmur Tbk",
    "KLBF.JK": "Kalbe Farma Tbk",
    "HMSP.JK": "HM Sampoerna Tbk",
    "GGRM.JK": "Gudang Garam Tbk",
    "SMGR.JK": "Semen Indonesia Tbk",
    "UNTR.JK": "United Tractors Tbk",
    "EXCL.JK": "XL Axiata Tbk",
    "PGAS.JK": "Perusahaan Gas Negara Tbk"
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