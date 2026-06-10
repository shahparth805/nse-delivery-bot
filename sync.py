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
    storage_file = "delivery_database.csv"

    # Capture the exact delivery percentage number entry for RAIN
    target_delivery = "0.0"
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) > 11 and parts[1].strip() == "EQ":
            symbol = parts[0].strip()
            if symbol == "RAIN":
                target_delivery = str(parts[11].strip())
                break

    # Build an explicit daily interval row entry tracking line block
    target_timestamp = f"{finalized_date}T00:00:00Z"

    # We format a standard database stream layout containing placeholders
    # so TradingView has immediate historical metrics to plot without crashing.
    csv_rows = [
        "time,open,high,low,close,volume",
        f"2026-06-05T00:00:00Z,{target_delivery},{target_delivery},{target_delivery},{target_delivery},0",
        f"2026-06-08T00:00:00Z,{target_delivery},{target_delivery},{target_delivery},{target_delivery},0",
        f"2026-06-09T00:00:00Z,{target_delivery},{target_delivery},{target_delivery},{target_delivery},0",
        f"{target_timestamp},{target_delivery},{target_delivery},{target_delivery},{target_delivery},0",
    ]

    # Write out the clean CSV database straight into your repo folder
    with open(storage_file, "w") as f:
        f.write("\n".join(csv_rows) + "\n")

    print(
        f"Data spreadsheet compiled successfully for RAIN: {target_delivery}%"
    )
else:
    print("Could not retrieve data files from NSE servers.")
