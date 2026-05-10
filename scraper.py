import requests
import pandas as pd
import os
from datetime import datetime, timedelta

# 確定的新竹市政府 JSON 網址
URL = "https://hispark.hccg.gov.tw/OpenData/GetParkInfo?format=json"
OUTPUT_FILE = "parking_history.csv"

def fetch_data():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return None
            
        data_json = response.json()
        parking_list = []
        
        tw_time = datetime.utcnow() + timedelta(hours=8)
        current_time = tw_time.strftime("%Y-%m-%d %H:%M:%S")
        
        if isinstance(data_json, list):
            for item in data_json:
                # 這裡修正了 Key 的名稱，對應新竹市政府最新的 JSON 格式
                # 同時處理大小寫可能變動的問題
                name = item.get('parkName') or item.get('ParkName')
                total = item.get('totalSpace') or item.get('TotalSpace')
                surplus = item.get('surplusSpace') or item.get('SurplusSpace')
                address = item.get('address') or item.get('Address')
                
                if name:
                    parking_list.append({
                        "Time": current_time,
                        "Name": name,
                        "Total": total,
                        "Surplus": surplus,
                        "Address": address
                    })
        
        print(f"[{current_time}] 偵測到 {len(parking_list)} 筆資料")
        return parking_list
    except Exception as e:
        print(f"抓取失敗: {e}")
        return None

# 執行邏輯
new_data = fetch_data()
if new_data:
    df_new = pd.DataFrame(new_data)
    
    # 存檔邏輯：如果是空的或沒檔案就直接寫，有的話就附加
    if os.path.exists(OUTPUT_FILE):
        try:
            # 讀取舊資料，若舊資料全是空的就直接覆蓋
            df_old = pd.read_csv(OUTPUT_FILE)
            if df_old.dropna(how='all', subset=['Name']).empty:
                df_final = df_new
            else:
                df_final = pd.concat([df_old, df_new], ignore_index=True)
        except:
            df_final = df_new
    else:
        df_final = df_new
    
    df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print("資料更新成功！")
