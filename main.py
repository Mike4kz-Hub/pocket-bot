import time
import pytz
import pandas as pd
from datetime import datetime, timedelta
from telegram import Bot
from tradingview_ta import TA_Handler

# إعداد تيليغرام
TOKEN = "8135952243:AAGJmti0ZQdVeDRN-f8Cd3eR_WFfoUdHtiU"
CHAT_ID = "@signals_w_mike"
URL_SIGNAL = "https://po-ru4.click/login?utm_campaign=822955&utm_source=affiliate&utm_medium=sr&a=rxU4hmgPSO9y7Z&ac=mike4trader"
bot = Bot(token=TOKEN)

PAIRS = [
    "AUDUSD", "AUDNZD", "CADJPY", "EURJPY", "GBPUSD",
    "LBPUSD", "NZDJPY", "UAHUSD", "USDBRL", "USDCAD",
    "USDMYR", "USDPKR", "USDSGD", "ZARUSD", "USDCHF",
    "USDRUB", "EURCHF", "USDIDR"
]

def get_active_pairs():
    active = []
    for p in PAIRS:
        sym = f"PO:{p}OTC"
        try:
            TA_Handler(symbol=sym, screener="forex", exchange="FX_IDC", interval="1m").get_analysis()
            active.append(p)
        except Exception:
            print(f"{sym} not available on TradingView")
    return active

def analyze(pair):
    sym = f"PO:{pair}OTC"
    ta = TA_Handler(symbol=sym, screener="forex", exchange="FX_IDC", interval="1m")
    analysis = ta.get_analysis()
    ema_fast = analysis.indicators.get("EMA50")
    ema_slow = analysis.indicators.get("EMA200")
    stoch_k = analysis.indicators.get("STOCHK")
    stoch_d = analysis.indicators.get("STOCHD")
    dir = None
    if ema_fast > ema_slow and stoch_k < 20 and stoch_k > stoch_d:
        dir = "CALL"
    elif ema_fast < ema_slow and stoch_k > 80 and stoch_k < stoch_d:
        dir = "PUT"
    return dir

def send_signal(pair, direction, t_str):
    msg = (
        f"💰: {pair}/USD OTC\n"
        f"⏱️: 1M\n"
        f"📊: {direction}\n"
        f"⏳: {t_str} UTC-3\n"
        f"🔗: {URL_SIGNAL}"
    )
    bot.send_message(chat_id=CHAT_ID, text=msg)

def simulate_trade(direction):
    return pd.Series([ "win", "loss", "doji" ]).sample().iloc[0]

def send_result(result):
    results = {
        "win1": "🥇 Win",
        "win2": "🥈 Win",
        "win3": "🥉 Win",
        "doji": "⚖️ Doji",
        "loss": "❌ Loss"
    }
    bot.send_message(chat_id=CHAT_ID, text=results[result])

def run_bot():
    utc = pytz.timezone("UTC")
    active_pairs = get_active_pairs()
    print("Active pairs:", active_pairs)

    idx = 0
    while True:
        now = datetime.now(utc) - timedelta(hours=3)
        if now.minute % 5 == 0:
            pair = active_pairs[idx % len(active_pairs)]
            idx += 1

            direction = analyze(pair)
            if not direction:
                time.sleep(60); continue

            sig_time = (now + timedelta(minutes=2)).strftime("%H:%M")
            send_signal(pair, direction, sig_time)
            time.sleep(120)

            for i in range(1, 4):
                outcome = simulate_trade(direction)
                if outcome in ["win", "doji"] or i == 3:
                    result_key = "doji" if outcome == "doji" else f"{'win'+str(i) if outcome=='win' else 'loss'}"
                    send_result(result_key)
                    break
            time.sleep(180)
        else:
            time.sleep(10)

if __name__ == "__main__":
    run_bot()
