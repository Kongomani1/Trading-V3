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

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("TELEGRAM_CHAT")

def send_telegram(msg):
    try:
        if not BOT_TOKEN or not CHAT_ID:
            print(f"BOT_TOKEN ou CHAT_ID manquant: BOT={bool(BOT_TOKEN)} CHAT={bool(CHAT_ID)}")
            return
        encoded = urllib.parse.quote(msg)
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={encoded}"
        urllib.request.urlopen(url, timeout=15).read()
        print(f"Envoyé Telegram: {msg[:60]}")
    except Exception as e:
        print(f"Erreur Telegram: {e}")

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
send_telegram(f"✅ V3 lancé à {datetime.now().strftime('%H:%M')} - Surveillance BTC/ETH en cours (Kinshasa)")

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
                if percent >= 0.5:
                    msg = f"🚀 ARBITRAGE {coin}\nBinance: {p_binance}\nBybit: {p_bybit}\nEcart: {percent:.2f}% ({diff:.2f}$)\nHeure: {datetime.now().strftime('%H:%M:%S')}"
                    send_telegram(msg)
        time.sleep(60)
    except Exception as e:
        print(f"Erreur boucle: {e}")
        time.sleep(30)
