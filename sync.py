import datetime
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
    storage_file = "delivery_database.json" # Kept JSON file extension to avoid altering run.yml config files
    
    # Extract the delivery metric explicitly for RAIN
    target_delivery = "0.0"
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) > 11 and parts[1].strip() == "EQ":
            symbol = parts[0].strip()
            if symbol == "RAIN":
                target_delivery = str(parts[11].strip())
                break

    # Build a flat, standard single key configuration block
    flat_payload = {
        "RAIN": target_delivery
    }

    # Save out the flat structural database
    import json
    with open(storage_file, "w") as f:
        json.dump(flat_payload, f, indent=2)
        
    print(f"Flat tracking stream saved successfully for data date: {finalized_date} with value {target_delivery}%")
else:
    print("Could not retrieve data files from NSE servers.")
