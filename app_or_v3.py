import os
from flask import Flask
import threading

web_app = Flask(__name__)
@web_app.route('/')
def home(): return "OR V3 Bot is LIVE"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web, daemon=True).start()
import urllib.request, urllib.parse, time, os
from datetime import datetime
MON_NUMERO = os.getenv("MON_NUMERO")
APIKEY = os.getenv("APIKEY")
def send_whatsapp(msg):
    try:
        url = f"https://api.callmebot.com/whatsapp.php?phone={MON_NUMERO}&text={urllib.parse.quote(msg)}&apikey={APIKEY}"
        urllib.request.urlopen(url, timeout=15).read()
    except Exception as e:
        print(e)
print("V3 demarree")
send_whatsapp(f"V3 lancee {datetime.now().strftime('%H:%M')}")
while True:
    time.sleep(60)
