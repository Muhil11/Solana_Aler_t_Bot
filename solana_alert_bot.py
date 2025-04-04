import requests
import pandas as pd
import time
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from datetime import datetime

# === CONFIG ===
BOT_TOKEN = "7644989892:AAFt2hVKSbEnKINEJ0HiKYyGKKLOEYUaH50"
CHAT_ID = "1871384395"
PAIR = "SOLUSDT"
BASE_INTERVAL = "5m"
CANDLE_LIMIT = 150

# === TELEGRAM ALERT ===
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)

# === FETCH BINANCE KLINES ===
def fetch_klines(interval):
    url = f"https://api.binance.com/api/v3/klines?symbol={PAIR}&interval={interval}&limit={CANDLE_LIMIT}"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=["time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "trades",
        "taker_buy_base", "taker_buy_quote", "ignore"])
    df["time"] = pd.to_datetime(df["time"], unit='ms')
    df.set_index("time", inplace=True)
    df = df.astype(float)
    return df[["open", "high", "low", "close", "volume"]]

# === SIGNAL CHECK ===
def check_signals():
    df_5m = fetch_klines("5m")
    df_15m = df_5m.resample("15min").agg({
        "open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"
    }).dropna()

    logs = []
    alert_triggered = False
    now_price = df_5m["close"].iloc[-1]

    # --- Indicators ---
    def indicators(df):
        rsi = RSIIndicator(df["close"], window=14).rsi().iloc[-1]
        ema9 = EMAIndicator(df["close"], window=9).ema_indicator()
        ema21 = EMAIndicator(df["close"], window=21).ema_indicator()
        crossover = ema9.iloc[-2] < ema21.iloc[-2] and ema9.iloc[-1] > ema21.iloc[-1]
        crossdown = ema9.iloc[-2] > ema21.iloc[-2] and ema9.iloc[-1] < ema21.iloc[-1]
        avg_vol = df["volume"].rolling(window=20).mean().iloc[-2]
        vol_spike = df["volume"].iloc[-1] > 2.5 * avg_vol

        # Reverse Engineered Band (deviation from EMA21)
        band_dev = 0.03 * ema21.iloc[-1]
        lower_band = ema21.iloc[-1] - band_dev
        upper_band = ema21.iloc[-1] + band_dev

        return {
            "rsi": rsi, "crossover": crossover, "crossdown": crossdown,
            "vol_spike": vol_spike, "ema21": ema21.iloc[-1],
            "lower_band": lower_band, "upper_band": upper_band
        }

    ind_5m = indicators(df_5m)
    ind_15m = indicators(df_15m)

    # --- BUY SIGNAL ---
    if (ind_5m["rsi"] < 30 or ind_5m["crossover"] or ind_5m["vol_spike"] or now_price < ind_5m["lower_band"]) and ind_15m["crossover"]:
        msg = f"\n🚀 *BUY Signal on SOL/USDT (5m + 15m)*\nPrice: `${now_price:.2f}`"
        if ind_5m["rsi"] < 30:
            msg += f"\n📉 RSI Oversold: `{ind_5m['rsi']:.2f}`"
        if ind_5m["crossover"]:
            msg += f"\n🔀 EMA 9/21 Bullish Crossover"
        if ind_5m["vol_spike"]:
            msg += f"\n📊 Volume Spike"
        if now_price < ind_5m["lower_band"]:
            msg += f"\n📈 Touched Lower Band: `{ind_5m['lower_band']:.2f}`"
        send_telegram_alert(msg)
        logs.append(f"[BUY] {datetime.now()} - {now_price}")
        alert_triggered = True

    # --- SELL SIGNAL ---
    if (ind_5m["rsi"] > 70 or ind_5m["crossdown"] or now_price > ind_5m["upper_band"]) and ind_15m["crossdown"]:
        msg = f"\n⚠️ *SELL Signal on SOL/USDT (5m + 15m)*\nPrice: `${now_price:.2f}`"
        if ind_5m["rsi"] > 70:
            msg += f"\n📈 RSI Overbought: `{ind_5m['rsi']:.2f}`"
        if ind_5m["crossdown"]:
            msg += f"\n🔻 EMA 9/21 Bearish Crossover"
        if now_price > ind_5m["upper_band"]:
            msg += f"\n📉 Touched Upper Band: `{ind_5m['upper_band']:.2f}`"
        send_telegram_alert(msg)
        logs.append(f"[SELL] {datetime.now()} - {now_price}")
        alert_triggered = True

    # --- Save Logs ---
    if alert_triggered:
        with open("alerts_log.txt", "a") as f:
            for line in logs:
                f.write(line + "\n")

# === LOOP ===
print("📡 Solana_Aler_t_Bot with Bands & Logs running...")
while True:
    try:
        check_signals()
        time.sleep(180)
    except Exception as e:
        print("Error:", e)
        time.sleep(60)