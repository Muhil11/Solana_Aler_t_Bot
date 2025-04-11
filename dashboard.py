import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Solana Alert Bot Dashboard", layout="wide")

# === 1. Load Local Data ===
@st.cache_data(ttl=30)
def load_local_data():
    df = pd.read_csv("solana_metrics_log.csv", header=None)
    df.columns = ["Timestamp", "TPS", "Block_Height", "BTC_DOM", "BTC_Hashrate"]
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values("Timestamp")
    return df

# === 2. Get Live SOL Price (CoinGecko) ===
@st.cache_data(ttl=30)
def get_sol_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
    try:
        data = requests.get(url).json()
        return float(data["solana"]["usd"])
    except:
        return None

# === 3. Trend Detection Helper ===
def detect_trend(series):
    if len(series) < 2:
        return "⏸️"
    return "📈" if series.iloc[-1] > series.iloc[-2] else "📉"

# === 4. Anomaly Detection ===
def detect_anomaly(series, threshold=0.2):
    if len(series) < 5:
        return ""
    avg = series[-5:].mean()
    current = series.iloc[-1]
    if abs(current - avg) / avg > threshold:
        return "🚨"
    return ""

# === Load Data ===
df = load_local_data()
df["TPS_7MA"] = df["TPS"].rolling(window=7).mean()
df["TPS_14MA"] = df["TPS"].rolling(window=14).mean()

# === Layout ===
st.title("📊 Solana Alert Bot — Analytics Dashboard")
latest = df.iloc[-1]
sol_price = get_sol_price()

# === Metrics Row ===
st.subheader("📌 Latest Metrics with Trends")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("TPS", f"{latest['TPS']}", help="Transactions Per Second")
col2.metric("Block Height", f"{int(latest['Block_Height'])}")
col3.metric("BTC Dominance", f"{latest['BTC_DOM']:.2f}%", detect_trend(df["BTC_DOM"]))
col4.metric("BTC Hashrate", f"{latest['BTC_Hashrate']:.2f} TH/s", detect_trend(df["BTC_Hashrate"]))
col5.metric("SOL Price (USD)", f"${sol_price:.2f}" if sol_price else "N/A", detect_trend(pd.Series([sol_price])))

# === TPS Chart with MA & Anomaly ===
st.subheader("⚡ TPS with Moving Averages & Volatility Alerts")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["Timestamp"], df["TPS"], label="TPS", linewidth=1.5)
ax.plot(df["Timestamp"], df["TPS_7MA"], label="7-MA", linestyle="--")
ax.plot(df["Timestamp"], df["TPS_14MA"], label="14-MA", linestyle=":")
ax.set_xlabel("Time")
ax.set_ylabel("TPS")
ax.legend()

# Anomaly alert on latest TPS
if detect_anomaly(df["TPS"]) == "🚨":
    st.error("⚠️ Sudden TPS Spike/Drop Detected!")

st.pyplot(fig)

# === BTC DOM Chart ===
st.subheader("🟠 BTC Dominance Over Time")
st.line_chart(df.set_index("Timestamp")["BTC_DOM"])

# === Hashrate Chart ===
st.subheader("🧮 BTC Hashrate Over Time")
st.line_chart(df.set_index("Timestamp")["BTC_Hashrate"])

# === SOL Price with Supply/Demand Zones ===
st.subheader("🪙 SOL Price — Supply/Demand Zones")

if sol_price:
    demand_zone = (80, 95)
    supply_zone = (130, 150)

    fig2, ax2 = plt.subplots(figsize=(10, 3))
    ax2.axhspan(*demand_zone, color='green', alpha=0.3, label="Demand Zone")
    ax2.axhspan(*supply_zone, color='red', alpha=0.3, label="Supply Zone")
    ax2.plot(df["Timestamp"], [sol_price] * len(df), label="SOL Price", color="blue", linewidth=2)
    ax2.set_ylabel("USD")
    ax2.legend()
    st.pyplot(fig2)

    # Zone Alert
    if demand_zone[0] <= sol_price <= demand_zone[1]:
        st.success("💰 SOL in Demand Zone — Potential Buy Opportunity")
    elif supply_zone[0] <= sol_price <= supply_zone[1]:
        st.warning("🚨 SOL in Supply Zone — Caution: Price Overhead")

else:
    st.warning("⚠️ Couldn't fetch live SOL price")

