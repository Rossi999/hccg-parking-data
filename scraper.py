import requests
import pandas as pd
import os
from datetime import datetime, timedelta

# 改用新竹市政府 JSON 資料源 (此格式比 XML 穩定且好解析)
URL = "https://hispark.hccg.gov.tw/OpenData/GetParkInfo"
OUTPUT_FILE = "parking_history.csv"

def fetch_data():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # 增加 verify=False 避免某些政府網站 SSL 證書過期導致報錯
        response = requests.get(URL, headers=headers, timeout=30, verify=True)
        
        # 檢查是否成功
        if response.status_code != 200:
            print(f"伺服器回應錯誤: {response.status_code}")
            return None
            
        # 嘗試解析 JSON
        data_json = response.json()
        parking_list = []
        
        tw_time = datetime.utcnow() + timedelta(hours=8)
        current_time = tw_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # 如果 JSON 是列表格式
        if isinstance(data_json, list):
            for item in data_json:
                parking_list.append({
                    "Time": current_time,
                    "Name": item.get('parkName'),
                    "Total": item.get('totalSpace'),
                    "Surplus": item.get('surplusSpace'),
                    "Address": item.get('address')
                })
        
        print(f"[{current_time}] 成功偵測到 {len(parking_list)} 筆資料")
        return parking_list
    except Exception as e:
        print(f"抓取失敗: {e}")
        return None

# 執行與存檔
new_data = fetch_data()
if new_data and len(new_data) > 0:
    df_new = pd.DataFrame(new_data)
    if os.path.exists(OUTPUT_FILE):
        df_old = pd.read_csv(OUTPUT_FILE)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_final = df_new
    df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print("資料更新成功！")
else:
    print("警告：本次仍未取得資料，請檢查網址或稍後再試。")
