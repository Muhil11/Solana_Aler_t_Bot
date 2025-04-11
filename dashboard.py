import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import requests

st.set_page_config(page_title="Solana Alert Dashboard", layout="wide")
st.title("📊 Solana Real-Time Metrics Dashboard")

# === Auto-refresh ===
st.caption("⏱ Auto-refreshing every 30 seconds")
st.button("🔄 Refresh Data")
time.sleep(30)
st.experimental_rerun()

# === Function to Get SOL Price ===
def get_sol_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
        data = requests.get(url).json()
        return data["solana"]["usd"]
    except:
        return None

# === Load Logged CSV Data ===
try:
    df = pd.read_csv("solana_metrics_log.csv", names=["Time", "TPS", "Block", "BTC Dominance", "BTC Hashrate"])
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.sort_values("Time")
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# === Show Latest Metrics ===
latest = df.iloc[-1]
st.metric("🔥 Current TPS", latest["TPS"])
st.metric("📦 Latest Block Height", int(latest["Block"]))
st.metric("🪙 BTC Dominance", f"{latest['BTC Dominance']:.2f}%")
st.metric("⚡ BTC Hashrate", f"{latest['BTC Hashrate']:.2f} TH/s")

# === Line Charts ===
st.subheader("📈 Historical Metrics")

col1, col2 = st.columns(2)

with col1:
    st.write("Solana TPS Over Time")
    st.line_chart(df.set_index("Time")["TPS"])

with col2:
    st.write("BTC Dominance Over Time")
    st.line_chart(df.set_index("Time")["BTC Dominance"])

st.write("BTC Hashrate Over Time")
st.line_chart(df.set_index("Time")["BTC Hashrate"])

# === SOL Price + Alerts ===
st.subheader("🔔 Price Alerts + Zones")

sol_price = get_sol_price()
if sol_price:
    st.info(f"💰 Current SOL Price: **${sol_price}**")

    # Zone Logic
    supply_zone = (160, 180)
    demand_zone = (100, 120)

    if supply_zone[0] <= sol_price <= supply_zone[1]:
        st.warning(f"⚠️ **Supply Zone Alert!** Price is in resistance range (${supply_zone[0]} - ${supply_zone[1]})")
    elif demand_zone[0] <= sol_price <= demand_zone[1]:
        st.success(f"📉 **Demand Zone Alert!** Price is in support range (${demand_zone[0]} - ${demand_zone[1]})")
    else:
        st.write("✅ Price is in a neutral zone.")
else:
    st.error("❌ Failed to fetch SOL price.")
