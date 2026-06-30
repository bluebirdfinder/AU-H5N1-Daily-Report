# -*- coding: utf-8 -*-
"""
H5N1 澳洲疫情自動追蹤與報告編譯引擎
功能：自動爬取澳洲農業部 (DAFF) 最新公告，更新病例資料庫，並動態寫入 HTML 報告範本中。
"""

import os
import sys
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

# 確保控制台輸出編碼為 UTF-8，避免 Windows 終端機 (CP950) 因 Emoji 或特殊字元而 UnicodeEncodeError
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ==================== 1. 基礎病例資料庫 (包含 2026 年 6 月最新 6 例) ====================
# 當爬蟲執行時，會以這個結構為基礎，並嘗試與官網最新發布的文字進行比對與動態修正。
DEFAULT_CASES = [
    {
        "id": "CASE-001",
        "type": "Confirmed",  # 狀態：Confirmed (確診) / Suspect (疑似) / Negative (陰性排除)
        "species": "褐賊鷗 (Brown Skua)",
        "location": "西澳埃斯佩蘭斯 Cape Le Grand 國家公園",
        "latitude": -33.9912,
        "longitude": 122.1481,
        "found_date": "2026-06-15",
        "notify_date": "2026-06-19",
        "confirm_date": "2026-06-20",
        "notes": "全澳洲官方首宗確診高致病性 H5N1 案例。由西澳與國家實驗室 (ACDP) 快速檢測確診。"
    },
    {
        "id": "CASE-002",
        "type": "Confirmed",
        "species": "南方巨鸌 (Southern Giant Petrel)",
        "location": "西澳埃斯佩蘭斯地區 (東部海岸線)",
        "latitude": -33.8613,
        "longitude": 121.9021,
        "found_date": "2026-06-18",
        "notify_date": "2026-06-20",
        "confirm_date": "2026-06-22",
        "notes": "西澳第二例確診，均位於 Esperance 地緣隔離之南部候鳥棲息帶。"
    },
    {
        "id": "CASE-003",
        "type": "Confirmed",
        "species": "巨鸌 (Giant Petrel)",
        "location": "南澳 Fleurieu 半島 Knights Beach",
        "latitude": -35.5325,
        "longitude": 138.6214,
        "found_date": "2026-06-14",  # 早被收容，但較晚進行官方通報
        "notify_date": "2026-06-19",
        "confirm_date": "2026-06-24",
        "notes": "南澳首宗野鳥確診案。與西澳案例空間隔離超過 1,000 公里，證明為零星候鳥迷途登陸點。"
    },
    {
        "id": "CASE-004",
        "type": "Confirmed",  # 6月27日已由官網正式宣告確診
        "species": "巨鸌 (Giant Petrel)",
        "location": "西澳丹斯伯勒 (Dunsborough) 地區",
        "latitude": -33.6128,
        "longitude": 115.1012,
        "found_date": "2026-06-22",
        "notify_date": "2026-06-24",
        "confirm_date": "2026-06-27",
        "notes": "原為疑似病例，於 6 月 27 日經聯邦首席獸醫官 Beth Cookson 正式發表聲明確診為第 4 起案件。"
    },
    {
        "id": "CASE-005",
        "type": "Suspect",  # 仍維持在疑似狀態，正待 ACDP 複檢
        "species": "巨鸌 (Giant Petrel)",
        "location": "西澳 Roses Beach (埃斯佩蘭斯西側)",
        "latitude": -33.8752,
        "longitude": 121.7915,
        "found_date": "2026-06-25",
        "notify_date": "2026-06-26",
        "confirm_date": "進行中 (Pending)",
        "notes": "西澳埃斯佩蘭斯西側 Roses Beach 發現之疑似陽性案例，檢體已送抵 ACDP 實驗室覆核中。"
    },
    {
        "id": "CASE-006",
        "type": "Negative",  # 經 PIRSA 正式排除
        "species": "死亡海鳥 (2隻)",
        "location": "南澳 Fowlers Bay Beach",
        "latitude": -31.9912,
        "longitude": 132.4331,
        "found_date": "2026-06-18",
        "notify_date": "2026-06-18",
        "confirm_date": "陰性 (已排除)",
        "notes": "南澳 Fowlers Bay 發現之海鳥屍體，經南澳農業廳 (PIRSA) PCR 檢測證實為陰性，成功排除禽流感嫌疑。"
    }
]

def fetch_daff_updates():
    """
    從澳洲農業部官網 (DAFF) 爬取最新資訊，並嘗試對現存案例進行狀態升級。
    """
    url = "https://www.agriculture.gov.au/node/26086"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print(f"正在連線澳洲農業部官網: {url} ...")
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"警告: 官網連線失敗 (HTTP status {response.status_code})。將採用基礎資料庫編譯。")
            return DEFAULT_CASES
        
        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text()
        
        # 建立深層複製，避免影響預設資料
        cases = json.loads(json.dumps(DEFAULT_CASES))
        
        # 爬蟲自動化比對規則 (1)：比對 Roses Beach 案例是否已經確診
        # 如果網頁文字中包含 "confirm"、"Roses Beach" 且不再是單純的 "suspect"，則代表狀態更新了
        if "Roses Beach" in page_text:
            # 尋找是否在 Roses Beach 案例的段落裡有 confirmed 關鍵字
            roses_paragraphs = [p.text for p in soup.find_all(["p", "li"]) if "Roses Beach" in p.text]
            for p in roses_paragraphs:
                if any(kw in p.lower() for kw in ["confirmed", "has confirmed", "tests confirmed"]):
                    for case in cases:
                        if case["id"] == "CASE-005":
                            if case["type"] != "Confirmed":
                                case["type"] = "Confirmed"
                                # 取得台北時間
                                now_taipei = datetime.now(timezone.utc) + timedelta(hours=8)
                                case["confirm_date"] = now_taipei.strftime("%Y-%m-%d")
                                case["notes"] = "原西澳 Roses Beach 疑似病例，經 ACDP 國家實驗室進一步檢測，官方已正式升級為確診病例。"
                                print("[動態更新] 偵測到 Roses Beach 疑似病例 (CASE-005) 已轉為『確診』狀態！")
                                
        # 爬蟲自動化比對規則 (2)：偵測是否有新的數字案例 (例如 "fifth confirmed case", "sixth confirmed case")
        # 藉此提醒管理團隊有突破性新病例爆發
        case_mentions = re.findall(r"(\w+)\s+(?:confirmed|H5N1)\s+case", page_text, re.IGNORECASE)
        if case_mentions:
            print(f"偵測到網頁提及病例數量關鍵字: {set(case_mentions)}")
            
        return cases

    except Exception as e:
        print(f"網路爬蟲發生例外錯誤: {str(e)}。將安全回退使用內置最安全資料庫編譯。")
        return DEFAULT_CASES

def main():
    # 1. 抓取最新病例數據
    cases_data = fetch_daff_updates()
    
    # 2. 依照「官方通報/採樣日期」由先至後進行排序 (Ascending Chronological Order)
    # 這樣能完美還原官方介入的疫情發展史
    cases_data.sort(key=lambda x: x["notify_date"])
    
    # 3. 讀取網頁模板檔案 (report_template.html)
    template_path = "report_template.html"
    output_path = "index.html"
    
    if not os.path.exists(template_path):
        print(f"嚴重錯誤：找不到模板檔案 '{template_path}'，請確認模板是否存在儲存庫根目錄！")
        return
        
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()
    
    # 4. 將最新的病例數據 JSON 注入模板預留的佔位符中，並將模板中原有的預設 JavaScript 陣列完全替換
    cases_json_str = json.dumps(cases_data, ensure_ascii=False, indent=2)
    updated_html = re.sub(
        r'/\* CASES_DATABASE_PLACEHOLDER \*/\s*\[.*?\]\s*;', 
        f"/* CASES_DATABASE_PLACEHOLDER */ {cases_json_str};", 
        html_template, 
        flags=re.DOTALL
    )
    
    # 5. 更新最後編譯更新時間 (校正為台北時間與澳洲 AEST 時間)
    utc_now = datetime.now(timezone.utc)
    taipei_now = utc_now + timedelta(hours=8)
    aest_now = utc_now + timedelta(hours=10)
    time_string = f"{taipei_now.strftime('%Y-%m-%d %H:%M:%S')} (台北時間) / {aest_now.strftime('%Y-%m-%d %H:%M:%S')} (澳洲 AEST)"
    updated_html = updated_html.replace("<!-- COMPILE_TIME_PLACEHOLDER -->", time_string)
    
    # 6. 寫出為正式部署網頁 index.html
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(updated_html)
        
    print(f"網頁自動編譯成功！已順利生成最新 H5N1 戰略決策報告 '{output_path}'。")

if __name__ == "__main__":
    main()
