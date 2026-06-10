import datetime
import json
import os
import requests


def fetch_most_recent_data():
    headers = {"User-Agent": "Mozilla/5.0"}
    # Check back up to 5 days to handle weekends, market holidays, or midnight runs safely
    for lookback in range(6):
        target_date = datetime.date.today() - datetime.timedelta(days=lookback)

        # Skip checking Sundays and Saturdays entirely
        if target_date.weekday() in [5, 6]:
            continue

        date_str = target_date.strftime("%d%m%Y")
        nse_url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"

        print(f"Checking NSE server records for date: {target_date}...")
        response = requests.get(nse_url, headers=headers)

        if response.status_code == 200 and "SYMBOL" in response.text:
            print(f"Found active data file for: {target_date}!")
            return response.text, target_date.strftime("%Y-%m-%d")

    return None, None


# Run the data lookup routine
raw_data, finalized_date = fetch_most_recent_data()

if raw_data:
    lines = raw_data.split("\n")
    storage_file = "delivery_database.json"

    # Load existing historical JSON data if it exists, otherwise start fresh
    if os.path.exists(storage_file):
        with open(storage_file, "r") as f:
            try:
                master_database = json.load(f)
            except:
                master_database = {}
    else:
        master_database = {}

    # Parse the rows directly from the exchange sheet
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) > 11 and parts[1].strip() == "EQ":
            symbol = parts[0].strip()
            try:
                del_pct = float(parts[11].strip())

                if symbol not in master_database:
                    master_database[symbol] = []

                # Append the validated data points
                master_database[symbol].append([finalized_date, del_pct])

                # Clean out any duplicate entries if run multiple times
                seen_dates = set()
                unique_entries = []
                for entry in sorted(
                    master_database[symbol], key=lambda x: x[0]
                ):
                    if entry[0] not in seen_dates:
                        seen_dates.add(entry[0])
                        unique_entries.append(entry)
                master_database[symbol] = unique_entries
            except:
                continue

    # Save out the master tracking matrix straight into our GitHub repository folder
    with open(storage_file, "w") as f:
        json.dump(master_database, f, indent=2)

    print(f"Master database updated successfully for data date: {finalized_date}")
else:
    print("Could not retrieve any recent data files from NSE servers.")
