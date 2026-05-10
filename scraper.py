import requests
import xml.etree.ElementTree as ET
import pandas as pd
import os
from datetime import datetime, timedelta

# 1. 設定
URL = "https://hispark.hccg.gov.tw/OpenData/GetParkInfo"
OUTPUT_FILE = "parking_history.csv"

def fetch_data():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        # 解析 XML
        root = ET.fromstring(response.text)
        
        # 台灣時間 UTC+8
        tw_time = datetime.utcnow() + timedelta(hours=8)
        current_time = tw_time.strftime("%Y-%m-%d %H:%M:%S")
        
        parking_list = []
        
        # 使用通配符 {*} 忽略 Namespace 影響
        for table in root.findall('.//{*}Table'):
            data = {
                "Time": current_time,
                "Name": table.findtext('{*}parkName'),
                "Total": table.findtext('{*}totalSpace'),
                "Surplus": table.findtext('{*}surplusSpace'),
                "Address": table.findtext('{*}address')
            }
            if data["Name"]: # 確保抓到名稱才加入
                parking_list.append(data)
        
        print(f"[{current_time}] 成功偵測到 {len(parking_list)} 筆資料")
        return parking_list
    except Exception as e:
        print(f"抓取失敗: {e}")
        return None

# 2. 執行與存檔
new_data = fetch_data()
if new_data:
    df_new = pd.DataFrame(new_data)
    
    # 檢查舊檔案
    if os.path.exists(OUTPUT_FILE):
        try:
            df_old = pd.read_csv(OUTPUT_FILE)
            df_final = pd.concat([df_old, df_new], ignore_index=True)
        except:
            df_final = df_new
    else:
        df_final = df_new
    
    # 存檔 (utf-8-sig 讓 Excel 不亂碼)
    df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print("資料更新成功！")
else:
    print("警告：本次未取得任何資料")
