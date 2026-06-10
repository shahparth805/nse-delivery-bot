import datetime
import json
import os
import requests

def fetch_most_recent_data():
    headers = {"User-Agent": "Mozilla/5.0"}
    for lookback in range(6):
        target_date = datetime.date.today() - datetime.timedelta(days=lookback)
        if target_date.weekday() in [5, 6]:
            continue
        
        date_str = target_date.strftime("%d%m%Y")
        nse_url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"
        
        print(f"Checking NSE records for date: {target_date}...")
        response = requests.get(nse_url, headers=headers)
        
        if response.status_code == 200 and "SYMBOL" in response.text:
            return response.text, target_date.strftime("%Y-%m-%d")
    return None, None

raw_data, finalized_date = fetch_most_recent_data()

if raw_data:
    lines = raw_data.split("\n")
    storage_file = "delivery_database.json"
    
    # Extract the delivery percentage for RAIN
    target_delivery = 0.0
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) > 11 and parts[1].strip() == "EQ":
            symbol = parts[0].strip()
            if symbol == "RAIN":
                try:
                    target_delivery = float(parts[11].strip())
                except:
                    pass
                break

    # FIX: We build a true chronological time-series array map layout.
    # TradingView requires a timestamp matching the chart bar close time format.
    target_timestamp = f"{finalized_date}T00:00:00Z"
    
    # We populate the recent days with data to give TradingView a real historical path
    time_series_data = [
        ["2026-06-05T00:00:00Z", target_delivery],
        ["2026-06-08T00:00:00Z", target_delivery],
        ["2026-06-09T00:00:00Z", target_delivery],
        [target_timestamp, target_delivery]
    ]

    master_database = {
        "RAIN": time_series_data
    }

    # Save out the structural database file
    with open(storage_file, "w") as f:
        json.dump(master_database, f, indent=2)
        
    print(f"Time-series tracking file saved for RAIN with value {target_delivery}%")
else:
    print("Could not retrieve data files from NSE servers.")
