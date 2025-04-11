# 📡 Solana_Aler_t_Bot

An advanced Telegram bot that sends **real-time trading signals** for **SOL/USDT** using technical indicators like RSI, EMA crossover, volume spikes, and dynamic support/resistance bands. Built with Python 🐍 and designed to run 24/7.

---

## 🚀 Features

- ✅ **BUY/SELL Alerts** using 5m and 15m multi-timeframe confirmation
- 📈 Detects:
  - RSI Oversold (<30) / Overbought (>70)
  - EMA 9/21 crossover (Bullish & Bearish)
  - Volume Spikes (2.5x rolling average)
  - Reversal near dynamic lower/upper bands (custom S/R)
- 🔁 Resampling logic to convert 5m candles into 15m trends
- 📤 Sends alerts directly to **Telegram**
- 🗂️ Historical logs saved in `alerts_log.txt`
- ⚡ Fast, lightweight, and cloud-deployable (e.g., Railway)

---

## 🛠️ Tech Stack

- Python 3.10+
- pandas
- requests
- ta (technical analysis)
- Telegram Bot API
- Binance Kline API

---

## 📦 Setup

1. Clone the repo:

```bash
git clone https://github.com/Muhil11/Solana_Aler_t_Bot.git
cd Solana_Aler_t_Bot
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your **Telegram Bot Token** and **Chat ID** in `solana_alert_bot.py`:

```python
BOT_TOKEN = "your_token"
CHAT_ID = "your_chat_id"
```

4. Run the bot:

```bash
python solana_alert_bot.py
```

---

## 📁 Files

- `solana_alert_bot.py` – Main bot script
- `requirements.txt` – Python packages
- `alerts_log.txt` – Alert history log
- `Procfile` – Required for Railway deployment

---

## ☁️ Deployment (Railway)

1. Push your code to GitHub.
2. Go to [https://railway.app](https://railway.app) and deploy from GitHub.
3. Add `python solana_alert_bot.py` in a `Procfile`.
4. Add `requirements.txt`.
5. It will run your bot 24/7 automatically.

---

## 💬 Example Alert

```
🚀 BUY Signal on SOL/USDT (5m + 15m)
Price: $142.35
📉 RSI Oversold: 28.52
🔀 EMA 9/21 Bullish Crossover
📊 Volume Spike
📈 Touched Lower Band: 141.88
```
⚠️ Important Notes
Always apply proper risk management when using this strategy, Only for education purpose.
---

## 🙌 Credits

Made with ❤️ to help crypto traders stay informed automatically.

---

```
