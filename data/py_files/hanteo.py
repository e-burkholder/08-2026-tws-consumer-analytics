import pandas as pd
import requests
import time
import os

# Curl->Python information from curlconverter (bash->python)
cookies = {
    'NEXT_LOCALE': 'en',
}

# List the different albums based on their ID
album_ids = ["900558280", #No Tragedy - TWS
             "900550075", #play hard - TWS
             "900530329", #SUMMER BEAT! - TWS
             "900560531", #II - RIIZE
             "900560088", #HOME- BND
             "900557987"  #Ode to Love - NCT WISH
]

# Create array to store all album data
all_data = []

# Loop through each album
for album_id in album_ids:
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,ko;q=0.8',
        'dnt': '1',
        'priority': 'u=1, i',
        'referer': f'https://www.hanteochart.com/en/albums/{album_id}',
        'user-agent': 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Mobile Safari/537.36',
    }   

    params = {
        'type': 'album',
        'term': 'real',
        'field': 'initial_value',
        'idx': album_id,
    }   

    # API Request & Exception Handeling
    try:
        response = requests.get(
            'https://www.hanteochart.com/api/chart-graph',
            params=params,
            cookies=cookies,
            headers=headers,
            timeout=30,
        )
    except requests.RequestException as e:
        print(f"Request failed for album: {album_id} with exception: {e}")
        time.sleep(2)
        continue

    # If response is valid, collect data & append as a row to all_data[]
    if response.status_code == 200:
        data = response.json()
        raw_list = data.get("data", data)

        target_names = raw_list.get('initialChartTargetName', [])
        album_name = target_names[0] if target_names else "Unknown Album"
        daily_sales = raw_list.get('initialChartListTarget', [])
        cum_sales = raw_list.get('initialChartListTargetStack', [])

        # Columns in the data
        col = {
            'Album_ID': album_id,
            'Album_Name': album_name
        }

        # Day column loop
        for num, sales in enumerate(daily_sales[:7], start=1):
            col[f"Day_{num}_Sales"] = sales

        # Add the last value in the Cumulative Sales array
        col['Cumulative_Sales'] = (
            cum_sales[6]
            if len(cum_sales) >= 7
            else (cum_sales[-1] if cum_sales else 0)
        )

        # Append completed data columns to all_data[] 
        all_data.append(col)
        print(f'Data for {album_name} retrieved')
        
    else:
        print(f"Error: Server returned status code for {album_id}, Status: {response.status_code}")

    # Pause program for 2 seconds (to prevent server disruptions)
    time.sleep(2)

# If all data has been collected, output to a CSV file
if all_data:
    final_df = pd.DataFrame(all_data)
    os.makedirs("data/csv_files", exist_ok=True)
    output_file = "data/csv_files/hanteo_data.csv"

    final_df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )
    print(f"Saved {len(final_df)} rows to {output_file}.")
else:
    print("No album data was collected.")    
