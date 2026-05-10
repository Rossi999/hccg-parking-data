import requests
import xml.etree.ElementTree as ET
import pandas as pd
import os
from datetime import datetime, timedelta

# 1. 抓取新竹市資料
URL = "https://hispark.hccg.gov.tw/OpenData/GetParkInfo"
OUTPUT_FILE = "parking_history.csv"

def fetch_data():
    try:
        response = requests.get(URL, timeout=30)
        root = ET.fromstring(response.content)
        parking_list = []
        
        # 轉換為台灣時間 (UTC+8)
        tw_time = datetime.utcnow() + timedelta(hours=8)
        current_time = tw_time.strftime("%Y-%m-%d %H:%M:%S")
        
        for table in root.findall('Table'):
            data = {
                "Time": current_time,
                "Name": table.findtext('parkName'),
                "Total": table.findtext('totalSpace'),
                "Surplus": table.findtext('surplusSpace'),
                "Address": table.findtext('address'),
                "X": table.findtext('wgsX'),
                "Y": table.findtext('wgsY')
            }
            parking_list.append(data)
        return parking_list
    except Exception as e:
        print(f"Error: {e}")
        return None

# 2. 儲存並累計資料
new_data = fetch_data()
if new_data:
    df_new = pd.DataFrame(new_data)
    if os.path.exists(OUTPUT_FILE):
        df_old = pd.read_csv(OUTPUT_FILE)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_final = df_new
    
    # 存回 CSV (utf-8-sig 讓 Excel 不亂碼)
    df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print("Data updated successfully!")
