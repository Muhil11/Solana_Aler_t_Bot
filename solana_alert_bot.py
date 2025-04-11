import requests
import csv
from datetime import datetime
from collections import deque
import time

# === Setup ===
TPS_API = "https://api.mainnet-beta.solana.com"
tps_history = deque(maxlen=20)  # For moving average

# === Log Data to CSV ===
def log_to_csv(tps, block_height, btc_dom, btc_hash):
    filename = "solana_metrics_log.csv"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([now, tps, block_height, btc_dom, btc_hash])

# === Get Solana TPS and Block Height ===
def get_solana_metrics():
    response = requests.post(
        TPS_API,
        json={"jsonrpc":"2.0","id":1,"method":"getRecentPerformanceSamples","params":[1]}
    )
    data = response.json()['result'][0]
    tps = (data['numTransactions'] / data['samplePeriodSecs'])
    block_height = data.get('slot', 0)
    return round(tps, 2), block_height

# === BTC Dominance ===
def get_btc_dominance():
    url = "https://api.coingecko.com/api/v3/global"
    try:
        data = requests.get(url).json()
        return data['data']['market_cap_percentage']['btc']
    except:
        return None

# === BTC Hashrate ===
def get_btc_hashrate():
    try:
        url = "https://api.blockchain.info/q/hashrate"
        return float(requests.get(url).text)
    except:
        return None

# === Get Solana Price ===
def get_sol_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
        data = requests.get(url).json()
        return data['solana']['usd']
    except:
        return None

# === Supply/Demand Zone Alert ===
def supply_demand_zone_alert(price):
    # You can tweak these zones based on market conditions
    demand_zone = (80, 95)
    supply_zone = (140, 160)

    if price and demand_zone[0] <= price <= demand_zone[1]:
        print(f"🟢 SOL in Demand Zone: ${price}")
    elif price and supply_zone[0] <= price <= supply_zone[1]:
        print(f"🔴 SOL in Supply Zone: ${price}")

# === Smart Alert Logic ===
def smart_alert(current_tps, btc_dom, btc_hash):
    tps_history.append(current_tps)
    if len(tps_history) == tps_history.maxlen:
        avg_tps = sum(tps_history) / len(tps_history)
        if current_tps < avg_tps * 0.85:
            print(f"⚠️ ALERT: TPS drop! Current: {current_tps}, Avg: {avg_tps:.2f}")

    if btc_dom and btc_dom > 55:
        print(f"⚠️ BTC Dominance High: {btc_dom:.2f}% — Market may be risk-off.")
    elif btc_dom and btc_dom < 45:
        print(f"📈 BTC Dominance Low: {btc_dom:.2f}% — Altcoins may rally.")

    if btc_hash and btc_hash < 200000:
        print(f"⚠️ BTC Hashrate Low: {btc_hash:.2f} TH/s — Network may be stressed.")

# === Main Loop ===
def main():
    print("🚀 Starting Solana Alert Bot with Analytics...")
    while True:
        try:
            tps, block_height = get_solana_metrics()
            btc_dom = get_btc_dominance()
            btc_hash = get_btc_hashrate()
            sol_price = get_sol_price()

            print(f"[{datetime.now().strftime('%H:%M:%S')}] TPS: {tps}, Block: {block_height}, BTC DOM: {btc_dom:.2f}%, Hashrate: {btc_hash:.2f} TH/s, SOL Price: ${sol_price}")

            log_to_csv(tps, block_height, btc_dom, btc_hash)
            smart_alert(tps, btc_dom, btc_hash)
            supply_demand_zone_alert(sol_price)

        except Exception as e:
            print("❌ Error:", e)

        time.sleep(30)  # Run every 30 seconds

if __name__ == "__main__":
    main()
