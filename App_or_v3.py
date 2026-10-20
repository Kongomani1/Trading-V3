import urllib.request, urllib.parse, time, os
from datetime import datetime

MON_NUMERO = os.getenv("MON_NUMERO")
APIKEY = os.getenv("APIKEY")

def send_whatsapp(msg):
    try:
        url = f"https://api.callmebot.com/whatsapp.php?phone={MON_NUMERO}&text={urllib.parse.quote(msg)}&apikey={APIKEY}"
        urllib.request.urlopen(url, timeout=15).read()
        print(f"Envoye: {msg}")
    except Exception as e:
        print(f"Erreur: {e}")

print("V3 demarree 24/7 sur Koyeb")
send_whatsapp(f"✅ V3 Scalper M5 lancée 24/7 sur Koyeb - {datetime.now().strftime('%H:%M')}")

while True:
    print("Bot en marche 24/7...")
    time.sleep(60)
