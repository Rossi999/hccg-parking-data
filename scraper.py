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
        # 增加 Header 模擬瀏覽器，避免被政府網站擋掉
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL, headers=headers, timeout=30)
        response.encoding = 'utf-8' # 強制使用 utf-8
        
        # 解析 XML
        root = ET.fromstring(response.content)
        parking_list = []
        
        # 轉換為台灣時間 (UTC+8)
        tw_time = datetime.utcnow() + timedelta(hours=8)
        current_time = tw_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # 尋找所有 Table 標籤
        tables = root.findall('.//Table')
        print(f"找到 {len(tables)} 筆資料")
        
        for table in tables:
            data = {
                "Time": current_time,
                "Name": table.findtext('parkName'),
                "Total": table.findtext('totalSpace'),
                "Surplus": table.findtext('surplusSpace'),
                "Address": table.findtext('address')
            }
            parking_list.append(data)
        return parking_list
    except Exception as e:
        print(f"抓取失敗: {e}")
        return None

# 2. 執行並儲存
new_data = fetch_data()

if new_data and len(new_data) > 0:
    df_new = pd.DataFrame(new_data)
    
    if os.path.exists(OUTPUT_FILE):
        # 讀取舊資料並合併
        df_old = pd.read_csv(OUTPUT_FILE)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_final = df_new
    
    # 存檔 (確保檔案一定會產生)
    df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"成功儲存資料至 {OUTPUT_FILE}")
else:
    # 如果沒抓到資料，建立一個空的 CSV 避免 Git 報錯
    if not os.path.exists(OUTPUT_FILE):
        df_empty = pd.DataFrame(columns=["Time", "Name", "Total", "Surplus", "Address"])
        df_empty.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print("未抓到資料，已建立空檔案")
