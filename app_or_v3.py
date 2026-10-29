import os
from flask import Flask
import threading
import urllib.request
import urllib.parse
import time
from datetime import datetime
import json

web_app = Flask(__name__)

@web_app.route('/')
def home(): return "OR V3 Bot is LIVE - Scanning"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web, daemon=True).start()

WON_NUMERO = os.getenv("WON_NUMERO")
API_KEY = os.getenv("API_KEY")

def send_whatsapp(msg):
    try:
        if not WON_NUMERO or not API_KEY: 
            print("WON_NUMERO ou API_KEY manquant")
            return
        encoded = urllib.parse.quote(msg)
        url = f"https://api.callmebot.com/whatsapp.php?phone={WON_NUMERO}&text={encoded}&apikey={API_KEY}"
        urllib.request.urlopen(url, timeout=15).read()
        print(f"Envoyé WhatsApp: {msg[:50]}")
    except Exception as e:
        print(f"Erreur WhatsApp: {e}")

def get_price_binance(symbol="BTCUSDT"):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        data = json.loads(urllib.request.urlopen(url, timeout=10).read())
        return float(data['price'])
    except: return None

def get_price_bybit(symbol="BTCUSDT"):
    try:
        url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}"
        data = json.loads(urllib.request.urlopen(url, timeout=10).read())
        return float(data['result']['list'][0]['lastPrice'])
    except: return None

print("V3 demarre - Systeme arbitrage active")
send_whatsapp(f"✅ V3 lancé à {datetime.now().strftime('%H:%M')} - Surveillance BTC/ETH en cours")

# Boucle principale d'arbitrage
while True:
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Scan en cours...")
        
        for coin in ["BTCUSDT", "ETHUSDT"]:
            p_binance = get_price_binance(coin)
            p_bybit = get_price_bybit(coin)
            
            if p_binance and p_bybit:
                diff = abs(p_binance - p_bybit)
                percent = (diff / p_binance) * 100
                
                print(f"{coin}: Binance={p_binance} Bybit={p_bybit} Diff={percent:.2f}%")
                
                if percent >= 0.5: # Alerte si > 0.5% d'écart
                    msg = f"🚀 ARBITRAGE {coin}\nBinance: {p_binance}\nBybit: {p_bybit}\nEcart: {percent:.2f}% ({diff:.2f}$)\nHeure: {datetime.now().strftime('%H:%M:%S')} Kinshasa"
                    send_whatsapp(msg)
        
        time.sleep(60) # scan toutes les 60 sec
        
    except Exception as e:
        print(f"Erreur boucle: {e}")
        time.sleep(30)
