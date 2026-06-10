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
        
        print(f"Checking NSE server records for date: {target_date}...")
        response = requests.get(nse_url, headers=headers)
        
        if response.status_code == 200 and "SYMBOL" in response.text:
            return response.text, target_date.strftime("%Y-%m-%d")
    return None, None

raw_data, finalized_date = fetch_most_recent_data()

if raw_data:
    lines = raw_data.split("\n")
    storage_file = "delivery_database.csv"
    
    # Read existing data rows to avoid losing history
    existing_rows = []
    if os.path.exists(storage_file):
        with open(storage_file, "r") as f:
            existing_rows = [line.strip() for line in f.readlines() if line.strip()]
    
    # If file is empty or brand new, create the header row
    if not existing_rows or not existing_rows[0].startswith("time"):
        existing_rows = ["time,open,high,low,close,volume"]
    
    today_timestamp = f"{finalized_date}T00:00:00Z"
    
    # Find RAIN or target stocks in the data stream
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) > 11 and parts[1].strip() == "EQ":
            symbol = parts[0].strip()
            
            # For this execution setup, let's capture the active ticker matching your chart
            if symbol == "RAIN":
                try:
                    del_pct = float(parts[11].strip())
                    # Format standard row matching TradingView custom feed configurations
                    new_csv_line = f"{today_timestamp},{del_pct},{del_pct},{del_pct},{del_pct},0"
                    
                    # Prevent adding duplicate rows if run multiple times
                    if not any(today_timestamp in row for row in existing_rows):
                        existing_rows.append(new_csv_line)
                except:
                    continue

    # Save data out as a clean csv spreadsheet
    with open(storage_file, "w") as f:
        f.write("\n".join(existing_rows) + "\n")
        
    print(f"Spreadsheet updated successfully for data date: {finalized_date}")
else:
    print("Could not retrieve data files from NSE servers.")
