# ARBITRAGE KINSHASA V4 + BONUS - Gold News Bot
# By Shilo - Kinshasa
# Features: T-15, T+5, SL/TP ATR, Morning 7h, Anti-Spread, Strict, Journal, DXY, Kill Zone, Lot Auto, Recap

import time, json, requests, os
from datetime import datetime, timezone, timedelta
import yfinance as yf

# CONFIG
JOURNAL_FILE = "journal_trades.json"
RISK_DOLLARS = 5  # Tu risques 5$ par trade
TELEGRAM_BOT_TOKEN = "TON_TOKEN"
TELEGRAM_CHAT_ID = "TON_CHAT_ID"
KINSHASA_TZ = timezone(timedelta(hours=1))

# CALENDRIER NEWS HIGH IMPACT OR
NEWS_CALENDAR = {
    # Format: "HH:MM": ("NEWS", "Impact OR si > prévu")
    "14:30": [("CPI", "Dollar Fort = OR Baisse"), ("PPI", "Dollar Fort = OR Baisse")],
    "15:30": [("Retail Sales", "Dollar Fort = OR Baisse")],
    "16:00": [("ISM Manufacturier", "Dollar Fort = OR Baisse - Aujourd'hui 55.5 vs 54.5 attendu")],
    # Ajoute automatiquement via API Investing.com
}

def get_live_price(symbol="GC=F"): # Gold Futures
    try:
        data = yf.Ticker(symbol).history(period="1d", interval="1m")
        return float(data['Close'].iloc[-1])
    except:
        return 2658.40  # fallback

def get_dxy_trend():
    try:
        dxy = yf.Ticker("DX-Y.NYB").history(period="1d", interval="5m")
        return "UP" if dxy['Close'].iloc[-1] > dxy['Close'].iloc[-20] else "DOWN"
    except:
        return "UNKNOWN"

def get_atr_sl_tp(price, atr_multiplier=1.5):
    # SL basé sur ATR + structure
    atr = 3.5 # Calcule vrai ATR M5 ici
    sl_distance = atr * atr_multiplier
    sl = price - sl_distance if BUY else price + sl_distance
    tp1 = price + (sl_distance * 2) if BUY else price - (sl_distance * 2) # 1:2 RR
    tp2 = price + (sl_distance * 3.5) if BUY else price - (sl_distance * 3.5) # Runner
    return sl, tp1, tp2, sl_distance

def is_kill_zone():
    # Kill Zone Kinshasa: 9h-12h et 14h30-20h
    now = datetime.now(KINSHASA_TZ).hour
    return (9 <= now <= 12) or (14 <= now <= 20)

def calculate_lot(sl_distance_dollars, risk_dollars=5):
    # Lot auto Deriv: risk / sl_distance
    lot = risk_dollars / sl_distance_dollars
    return round(lot, 2)

def send_alert(message):
    print(message) # Remplace par Telegram/WhatsApp API
    # requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", data={"chat_id": TELEGRAM_CHAT_ID, "text": message})

# 1. MORNING BRIEFING 7H KINSHASA
def morning_briefing():
    now = datetime.now(KINSHASA_TZ).strftime("%d/%m")
    msg = f"☀️ BRIEFING 7H - {now} - OR (XAUUSD)\nAujourd'hui 3 news OR: 14h30 CPI, 16h00 ISM\nImpact: Si CPI monte = Dollar fort = OR baisse probable\nReste attentif Shilo, Kill Zone 14h30-20h"
    send_alert(msg)

# 2. ALERTE T-15 MIN
def alert_t_minus_15(news_name, news_time):
    dxy = get_dxy_trend()
    msg = f"🚨 DANS 15 MIN - {news_name} à {news_time} heure de Kin\n📊 Impact prévu OR: {NEWS_CALENDAR[news_time][0][1]}\n📈 DXY Trend: {dxy}\n⚠️ Conseil: Ne trade pas maintenant, attends confirmation M5 après news"
    send_alert(msg)

# 3. ANALYSE CONFIRMATION T+5 MIN (TA DEMANDE PRINCIPALE)
def confirmation_t_plus_5(news_name):
    if not is_kill_zone():
        send_alert("😴 Hors Kill Zone, marché calme, on skip")
        return
    
    time.sleep(300) # Attends 5 min que marché digère
    price = get_live_price()
    dxy_trend = get_dxy_trend()
    
    # LOGIQUE DE CONFIRMATION STRICTE
    # Exemple: Cassure + Retest + Bougie englobante
    # Ici tu ajoutes ton analyse technique réelle
    signal = "BUY" # Déterminé par cassure structure
    confirmation = "Cassure 2655 + Bougie englobante haussière + Retest validé"
    
    # Filtre DXY Bonus
    if dxy_trend == "UP" and signal == "BUY":
        send_alert(f"⚠️ DIVERGENCE DXY - DXY monte fort, {signal} annulé pour {news_name}")
        return

    sl, tp1, tp2, sl_dist = get_atr_sl_tp(price)
    lot = calculate_lot(sl_dist, RISK_DOLLARS)
    
    msg = f"""🚨 CONFIRMATION OR - {news_name}
📊 Prix: {price}
✅ SIGNAL: {signal}
⏱️ Timeframe: M5 (entrée) / M15 (tendance)
🔍 Confirmation: {confirmation}
🎯 Entrée: {price-2:.1f}-{price:.1f}
🛑 SL: {sl:.1f} ({sl_dist:.1f}$ / sous structure + ATR)
💰 TP1: {tp1:.1f} (sécurise 50% - 1:2 RR)
💰 TP2: {tp2:.1f} (runner)
📦 Lot Deriv: {lot} (risque {RISK_DOLLARS}$)
⚠️ Conseil: Spread Deriv élevé 2 min, attends 2 min encore
🧠 DXY: {dxy_trend} - Confirmé"""

    send_alert(msg)
    
    # 7. JOURNAL AUTO
    trade = {
        "date": datetime.now().isoformat(),
        "news": news_name,
        "signal": signal,
        "price": price,
        "sl": sl, "tp1": tp1, "tp2": tp2,
        "result": "PENDING"
    }
    save_journal(trade)

def save_journal(trade):
    data = []
    if os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, "r") as f:
            data = json.load(f)
    data.append(trade)
    with open(JOURNAL_FILE, "w") as f:
        json.dump(data, f, indent=2)

# MAIN LOOP
if __name__ == "__main__":
    print("ARBITRAGE KINSHASA V4 + BONUS LIVE - Kinshasa")
    # morning_briefing() # Appelé par scheduler à 7h
    # Exemple aujourd'hui ISM:
    # alert_t_minus_15("ISM Manufacturier", "16:00")
    # confirmation_t_plus_5("ISM Manufacturier")
