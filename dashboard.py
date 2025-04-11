import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

CSV_FILE = "solana_metrics_log.csv"

st.set_page_config(page_title="Solana Alert Dashboard", layout="wide")
st.title("📊 Solana Realtime Metrics Dashboard")

# === Load Data ===
try:
    df = pd.read_csv(CSV_FILE, names=["timestamp", "TPS", "Block", "BTC_DOM", "BTC_HASH"], parse_dates=["timestamp"])
    df = df.dropna()
except FileNotFoundError:
    st.error("CSV log file not found.")
    st.stop()

# === Latest Metrics ===
latest = df.iloc[-1]
col1, col2, col3, col4 = st.columns(4)
col1.metric("⚡ TPS", latest["TPS"])
col2.metric("📦 Block Height", int(latest["Block"]))
col3.metric("🟠 BTC Dominance", f"{latest['BTC_DOM']:.2f}%")
col4.metric("🔧 BTC Hashrate", f"{latest['BTC_HASH']:.2f} TH/s")

# === Line Chart ===
st.subheader("TPS Over Time")
fig, ax = plt.subplots()
ax.plot(df["timestamp"], df["TPS"], label="TPS", color="blue")
ax.set_xlabel("Time")
ax.set_ylabel("TPS")
ax.grid(True)
st.pyplot(fig)

# === Alert Section ===
st.subheader("🔔 Alerts")
avg_tps = df["TPS"].tail(20).mean()
if latest["TPS"] < avg_tps * 0.85:
    st.error(f"⚠️ TPS Drop Detected! Current: {latest['TPS']}, Avg: {avg_tps:.2f}")
else:
    st.success("✅ TPS is within normal range.")

