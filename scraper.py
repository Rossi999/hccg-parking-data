import requests
import pandas as pd
import os
from datetime import datetime, timedelta

# 1. 設定新竹市政府提供的 JSON 網址
URL = "https://hispark.hccg.gov.tw/OpenData/GetParkInfo"
OUTPUT_FILE = "parking_history.csv"

def fetch_data():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # 強制要求 JSON 格式
        response = requests.get(URL, params={'format': 'json'}, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return None
            
        data_json = response.json()
        parking_list = []
        
        # 取得台灣時間
        tw_time = datetime.utcnow() + timedelta(hours=8)
        current_time = tw_time.strftime("%Y-%m-%d %H:%M:%S")
        
        if isinstance(data_json, list):
            for item in data_json:
                # 這裡完全對照你提供的官方欄位名稱 (全大寫)
                name = item.get('PARKINGNAME')
                total = item.get('TOTALQUANTITY')  # 總車位
                surplus = item.get('FREEQUANTITY') # 剩餘車位
                address = item.get('ADDRESS')
                
                if name:
                    parking_list.append({
                        "Time": current_time,
                        "Name": name,
                        "Total": total,
                        "Surplus": surplus,
                        "Address": address
                    })
        
        print(f"[{current_time}] 成功偵測到 {len(parking_list)} 筆資料")
        return parking_list
    except Exception as e:
        print(f"抓取失敗: {e}")
        return None

# 2. 執行並存檔
new_data = fetch_data()
if new_data:
    df_new = pd.DataFrame(new_data)
    
    if os.path.exists(OUTPUT_FILE):
        try:
            df_old = pd.read_csv(OUTPUT_FILE)
            # 💡 這一行很重要：把之前抓錯的（Name 欄位是空的）髒資料清掉
            df_old = df_old.dropna(subset=['Name'])
            df_final = pd.concat([df_old, df_new], ignore_index=True)
        except:
            df_final = df_new
    else:
        df_final = df_new
    
    # 存檔
    df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print("資料更新成功！")
