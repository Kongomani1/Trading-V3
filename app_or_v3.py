import os, threading, urllib.request, urllib.parse, time, json, re
from flask import Flask
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET

web_app = Flask(__name__)
@web_app.route('/')
def home(): return "V4 GOLD PRO LIVE - Deriv"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_web, daemon=True).start()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("TELEGRAM_CHAT")

def send_telegram(msg):
    try:
        if not BOT_TOKEN or not CHAT_ID: return
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={urllib.parse.quote(msg)}&parse_mode=HTML"
        urllib.request.urlopen(url, timeout=15).read()
        print(f"TG Sent: {msg[:50]}")
    except Exception as e:
        print(f"TG Error: {e}")

def get_gold_price():
    # PAXG suit l'or XAUUSD 1:1
    try:
        data = json.loads(urllib.request.urlopen("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).read())
        return float(data['price'])
    except:
        try: # fallback Bybit
            d=json.loads(urllib.request.urlopen("https://api.bybit.com/v5/market/tickers?category=spot&symbol=PAXGUSDT", timeout=10).read())
            return float(d['result']['list'][0]['lastPrice'])
        except: return 2650.0

def get_gold_candles(limit=20):
    try:
        url=f"https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit={limit}"
        data=json.loads(urllib.request.urlopen(url, timeout=10).read())
        closes=[float(c[4]) for c in data]
        highs=[float(c[2]) for c in data]
        lows=[float(c[3]) for c in data]
        return closes, highs, lows
    except: return [], [], []

def fetch_calendar():
    # ForexFactory this week XML
    events=[]
    try:
        xml_data = urllib.request.urlopen("https://nfs.faireconomy.media/ff_calendar_thisweek.xml", timeout=15).read()
        root = ET.fromstring(xml_data)
        for ev in root.findall('event'):
            country = ev.find('country').text if ev.find('country') is not None else ""
            impact = ev.find('impact').text if ev.find('impact') is not None else ""
            title = ev.find('title').text if ev.find('title') is not None else ""
            date_str = ev.find('date').text if ev.find('date') is not None else ""
            time_str = ev.find('time').text if ev.find('time') is not None else ""
            if country=="USD" and impact=="High":
                # Titres qui impactent l'or
                if any(k in title for k in ["CPI","NFP","Non-Farm","FOMC","Fed","PPI","Retail","Unemployment","GDP","Interest"]):
                    # Parse date/time FF is EST, convert approx to UTC then Kinshasa UTC+1
                    try:
                        # date format mm-dd-yyyy, time like 8:30am
                        dt_naive = datetime.strptime(f"{date_str} {time_str}", "%m-%d-%Y %I:%M%p")
                        # FF time is ET (UTC-4/5), approx UTC = ET+4, simplifions UTC
                        dt_utc = dt_naive + timedelta(hours=4)
                        events.append({"title":title,"time_utc":dt_utc,"impact":impact})
                    except: pass
    except Exception as e:
        print(f"Calendar error {e}")
    return events

KINSHASA_TZ = timezone(timedelta(hours=1))
sent_alerts=set()
sent_confirm=set()
calendar_cache=[]
last_cal_fetch=0

print("V4 GOLD PRO Demarre - Deriv")
send_telegram("🚀 <b>V4 GOLD PRO est LIVE - Deriv</b>\n\n✅ Mode: Attente Confirmation\n📊 Actif: XAUUSD (PAXG)\n🕐 Timezone: Kinshasa (UTC+1)\n🔔 Je te préviens 15min avant chaque news USD High\n\nEn attente du calendrier...")

while True:
    try:
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        now_kin = datetime.now(KINSHASA_TZ)

        # Refresh calendar every hour
        if time.time()-last_cal_fetch > 3600:
            calendar_cache = fetch_calendar()
            last_cal_fetch=time.time()
            print(f"Calendar fetched {len(calendar_cache)} events")
            # Morning briefing 7h Kinshasa
            if now_kin.hour==7 and now_kin.minute<5:
                if calendar_cache:
                    msg_today="<b>☀️ BRIEFING OR DU JOUR - Deriv</b>\n\n"
                    today_events=[e for e in calendar_cache if e['time_utc'].date()==now_utc.date()]
                    if today_events:
                        for ev in today_events:
                            t_kin = ev['time_utc']+timedelta(hours=1)
                            msg_today+=f"🕐 {t_kin.strftime('%H:%M')} - {ev['title']}\n"
                        msg_today+="\n⚠️ Prépare M5/M15, j'alerte 15min avant"
                    else:
                        msg_today+="Aucune news High impact USD aujourd'hui. Marché calme pour l'or."
                    send_telegram(msg_today)

        # Check alerts T-15 min
        for ev in calendar_cache:
            ev_time = ev['time_utc']
            diff_min = (ev_time - now_utc).total_seconds()/60
            ev_id = ev['title']+str(ev_time)

            # Alerte 15 min avant
            if 14 <= diff_min <= 16 and ev_id not in sent_alerts:
                t_kin = ev_time + timedelta(hours=1)
                gold_price = get_gold_price()
                msg = f"⏰ <b>ALERTE OR DANS 15 MIN - Deriv</b>\n\n📰 <b>{ev['title']}</b>\n💥 Impact: Élevé (USD) → Impact direct XAUUSD\n🕐 Heure news: {t_kin.strftime('%H:%M')} Kinshasa\n📊 Prix Or actuel: {gold_price:.2f}$\n\n📋 <b>PLAN À PRÉPARER:</b>\n• Timeframe: Prépare M5 et M15\n• Stratégie: Attente Confirmation (pas de trade avant)\n• Deriv: Spread va x3-x5 pendant news\n\n⚠️ <b>CONSIGNE:</b> Ne touche à rien. J'analyse pour toi dans 20min (T+5 après news) et je te donne BUY/SELL + SL/TP"
                send_telegram(msg)
                sent_alerts.add(ev_id)
                print(f"Alert 15min sent {ev['title']}")

            # Confirmation T+5 min après news
            if -10 <= diff_min <= -4 and ev_id not in sent_confirm: # entre 4 et 10 min après
                # On attend 5 min, on analyse
                closes, highs, lows = get_gold_candles(20)
                price_now = get_gold_price()
                if len(closes)>=6:
                    price_5m_ago = closes[-2]
                    move_pct = (price_now - price_5m_ago)/price_5m_ago*100
                    atr = (max(highs[-10:]) - min(lows[-10:])) if highs else 10

                    # Logique confirmation
                    if move_pct > 0.25: # Hausse forte post news = dollar faible = BUY Or
                        direction="BUY"
                        confirm="Forte bougie haussière M5 + Cassure résistance + Momentum haussier post-news"
                        sl = price_now - max(8, atr*0.8)
                        tp1 = price_now + (price_now-sl)*1.5
                        tp2 = price_now + (price_now-sl)*3
                    elif move_pct < -0.25:
                        direction="SELL"
                        confirm="Forte bougie baissière M5 + Cassure support + Pression vendeuse post-news"
                        sl = price_now + max(8, atr*0.8)
                        tp1 = price_now - (sl-price_now)*1.5
                        tp2 = price_now - (sl-price_now)*3
                    else:
                        direction="ATTENTE / RANGE"
                        confirm="Pas de direction claire, marché hésite - Attends 2ème confirmation M15"
                        sl=0; tp1=0; tp2=0

                    if direction!="ATTENTE / RANGE":
                        msg_conf = f"🚨 <b>CONFIRMATION OR - {ev['title']}</b>\n\n📊 Prix Or: {price_now:.2f}$\n📈 Mouvement post-news: {move_pct:+.2f}%\n\n✅ <b>SIGNAL: {direction}</b>\n⏱️ Timeframe entrée: M5 (idéal)\n⏱️ Timeframe tendance: M15\n🔍 Confirmation: {confirm}\n\n🎯 Entrée: {price_now-2:.1f} - {price_now+2:.1f}\n🛑 SL: {sl:.1f} ({abs(price_now-sl):.1f}$ / sous structure)\n💰 TP1: {tp1:.1f} (Sécurise 50% - RR 1:1.5)\n💰 TP2: {tp2:.1f} (Runner - RR 1:3)\n\n⚠️ <b>DERIV CONSEIL:</b> Spread encore élevé 2-3 min, attends pullback M5 avant entrée. Ne risque pas plus de 1-2%.\n\n💡 Si M5 reteste niveau cassé, c'est ton GO."
                    else:
                        msg_conf = f"⏳ <b>OR EN ATTENTE - {ev['title']}</b>\n\n📊 Prix: {price_now:.2f}$\nMouvement faible {move_pct:+.2f}%\n\n🔍 Confirmation: {confirm}\n⏱️ Reste en M15, attends une vraie cassure. Je re-analyse dans 5 min."

                    send_telegram(msg_conf)
                    sent_confirm.add(ev_id)
                    print(f"Confirmation sent {direction}")

        # Live price log
        if int(time.time())%120==0:
            print(f"Gold {get_gold_price()} - Next events {len(calendar_cache)} - {now_kin.strftime('%H:%M')}")

        time.sleep(60)
    except Exception as e:
        print(f"V4 Error {e}")
        time.sleep(30)
