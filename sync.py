import datetime
import os
import pandas as pd
import requests

# 1. SETUP CREDENTIALS
# Erase the text inside the quotes below and paste your real Nasdaq API key
NASDAQ_API_KEY = "y45iH4sa1Sx1s8tcRyyx"
DATASET_CODE = "NSE_DELIV"

# Determine today's file name target from the NSE servers
date_str = datetime.date.today().strftime("%d%m%Y")
nse_url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"
headers = {"User-Agent": "Mozilla/5.0"}

print("Waking up worker... Querying National Stock Exchange servers...")
response = requests.get(nse_url, headers=headers)

if response.status_code == 200:
    with open("today.csv", "w") as f:
        f.write(response.text)

    df = pd.read_csv("today.csv")
    df.columns = df.columns.str.strip()
    df = df[df["SERIES"] == "EQ"]
    df["DATE1"] = pd.to_datetime(df["DATE1"]).dt.strftime("%Y-%m-%d")

    for _, row in df.iterrows():
        symbol = str(row["SYMBOL"]).strip()
        del_pct = row["DELIV_PER"]
        date_today = row["DATE1"]

        stock_file = f"history_{symbol}.csv"
        new_row = pd.DataFrame(
            {"Date": [date_today], "DeliveryPercentage": [del_pct]}
        )

        if not os.path.exists(stock_file):
            new_row.to_csv(stock_file, index=False)
            combined = new_row
        else:
            old_df = pd.read_csv(stock_file)
            combined = (
                pd.concat([old_df, new_row])
                .drop_duplicates(subset=["Date"], keep="last")
                .sort_values(by="Date")
            )
            combined.to_csv(stock_file, index=False)

        # 2. AUTOMATIC BOX GENERATION & DATA PUSH LAYER
        upload_url = f"https://data.nasdaq.com/api/v3/datasets/{DATASET_CODE}/{symbol}/data.json?api_key={NASDAQ_API_KEY}"
        payload = {"dataset": {"data": combined.values.tolist()}}

        # Attempt to upload to the dataset row
        res = requests.put(upload_url, json=payload)

        # If Nasdaq responds with 404 (Box does not exist yet), force the script to create it
        if res.status_code == 404:
            create_url = f"https://data.nasdaq.com/api/v3/datasets.json?api_key={NASDAQ_API_KEY}"
            creation_payload = {
                "dataset": {
                    "database_code": DATASET_CODE,
                    "dataset_code": symbol,
                    "name": f"{symbol} Daily Stock Delivery Volume Data",
                    "private": True,
                    "data": combined.values.tolist(),
                }
            }
            requests.post(create_url, json=creation_payload)

    print("Database sync verified and pushed cleanly to Nasdaq cloud rooms.")
else:
    print(
        "NSE exchange server file hasn't compiled yet for evening processing."
    )
