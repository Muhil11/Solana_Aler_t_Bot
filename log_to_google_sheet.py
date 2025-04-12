import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Google Auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open your Google Sheet
sheet = client.open("Solana_Alert_Log").sheet1

def log_to_google_sheets(tps, block_height, btc_dom, btc_hash, sol_price):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [now, tps, block_height, btc_dom, btc_hash, sol_price]
    sheet.append_row(row)
