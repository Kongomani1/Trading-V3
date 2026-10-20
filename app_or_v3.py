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
