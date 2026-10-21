import os
from flask import Flask
import threading
import urllib.request
import urllib.parse
import time
from datetime import datetime

web_app = Flask(__name__)
@web_app.route('/')
def home(): return "OR V3 Bot is LIVE"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web, daemon=True).start()

WON_NUMERO = os.getenv("WON_NUMERO")
API_KEY = os.getenv("API_KEY")

def send_whatsapp(msg):
    try:
        url = f"https://api.callmebot.com/whatsapp.php?phone={WON_NUMERO}&text={urllib.parse.quote(msg)}&apikey={API_KEY}"
        urllib.request.urlopen(url, timeout=15).read()
    except Exception as e:
        print(e)

print("V3 demarre")
send_whatsapp(f"V3 lancee {datetime.now().strftime('%H:%M')}")
while True:
    time.sleep(60)
