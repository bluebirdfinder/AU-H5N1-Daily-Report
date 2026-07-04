# -*- coding: utf-8 -*-
"""
H5N1 澳洲疫情自動追蹤與報告編譯引擎 (全自動地理定位與動態摘要版)
功能：自動爬取澳洲農業部 (DAFF) 及 NSW DPIRD 官網最新公告，更新病例資料庫，
      自動透過 OpenStreetMap Nominatim API 對新地點進行地理定位，
      並依據當前數據動態產生包含超連結之官方事實與媒體觀察摘要，動態寫入 HTML 報告中。
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

# ==================== 1. 基礎病例資料庫 (包含 2026 年 6-7 月最新 7 例) ====================
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
    },
    {
        "id": "CASE-007",
        "type": "Suspect",  # 7月3日初步檢出
        "species": "巨鸌 (Giant Petrel)",
        "location": "新南威爾斯州 Hawks Nest (Newcastle 以北)",
        "latitude": -32.6658,
        "longitude": 152.1793,
        "found_date": "2026-07-02",
        "notify_date": "2026-07-03",
        "confirm_date": "進行中 (Pending)",
        "notes": "新南威爾斯州 (NSW) 首宗野鳥疑似病例。於 Hawks Nest 發現之巨鸌初步檢出呈 H5 陽性，檢體已送往 ACDP 國家實驗室進行 H5N1 確診覆核中。"
    }
]

def get_coordinates_from_api(location_name):
    """
    透過 OpenStreetMap Nominatim 免費地理編碼 API，將地名轉換為精確 GPS 經緯度
    """
    query = f"{location_name}, Australia"
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }
    # 依據 Nominatim 使用政策，必須聲明一個有意義且獨特之 User-Agent，避免被封鎖
    headers = {
        "User-Agent": "Purina-Blayney-H5N1-Monitor/1.0 (contact: bluebirdfinder@example.com)"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                display_name = data[0]["display_name"]
                print(f"[地理編碼成功] 地名: {location_name} -> 坐標: ({lat}, {lon})")
                return lat, lon
    except Exception as e:
        print(f"[地理編碼失敗] 無法解析地名 '{location_name}': {str(e)}")
    return None, None

def discover_new_cases(soup, existing_cases):
    """
    動態分析網頁 HTML，尋找潛在的全新疫情地點，並自動進行地理定位
    """
    if not soup:
        return []
        
    # 提取所有包含關鍵字之段落文字
    relevant_texts = []
    for elem in soup.find_all(["p", "li"]):
        txt = elem.text.strip()
        if any(kw in txt.lower() for kw in ["wild bird", "petrel", "skua", "seabird", "influenza", "h5n1", "h5", "detection"]):
            relevant_texts.append(txt)
            
    # 用正則表達式匹配地點特徵，例如 "near X"、"at X"、"in X"、"from X"
    # X 通常為 1-3 個大寫字母開頭之英文單字（如 Knights Beach, Hawks Nest）
    candidates = []
    for txt in relevant_texts:
        matches = re.findall(r"\b(near|at|in|from)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2})", txt)
        for prep, m in matches:
            m_clean = m.strip(",.() ")
            # 排除一些非地點之常見英文名詞與字詞
            if m_clean.lower() in ["australia", "western australia", "south australia", "new south wales", "victoria", 
                                  "queensland", "tasmania", "june", "july", "august", "september", "acdp", "csiro", 
                                  "emergency", "avian", "influenza", "h5n1", "h5", "the", "department", "giant", "southern"]:
                continue
            candidates.append((m_clean, txt))
            
    # 移除重複的候選地點
    unique_candidates = {}
    for loc, source_text in candidates:
        if loc not in unique_candidates:
            unique_candidates[loc] = source_text
            
    new_discovered = []
    case_idx = len(existing_cases) + 1
    
    for loc, src_txt in unique_candidates.items():
        # 1. 檢查是否已經存在於現有病例列表中 (用名字相似度或包含關係)
        is_existing = False
        for ec in existing_cases:
            if loc.lower() in ec["location"].lower() or ec["location"].lower() in loc.lower():
                is_existing = True
                break
        if is_existing:
            continue
            
        # 2. 呼叫地理編碼 API 獲取坐標
        print(f"[動態偵測] 發現全新潛在疫情地點關鍵字: '{loc}'，正在進行地理定位...")
        lat, lon = get_coordinates_from_api(loc)
        if lat is None or lon is None:
            continue  # 定位失敗，跳過
            
        # 3. 再次藉由坐標檢查是否為已知點的重複定位 (防止名字不同但經緯度極近，如 10 公里內)
        is_close = False
        for ec in existing_cases:
            dist = abs(ec["latitude"] - lat) + abs(ec["longitude"] - lon)
            if dist < 0.1:  # 約小於 10 公里
                is_close = True
                break
        if is_close:
            continue
            
        # 4. 判斷確診狀態
        type_status = "Suspect"
        confirm_date = "進行中 (Pending)"
        notes_prefix = "動態偵測疑似病例。"
        if any(kw in src_txt.lower() for kw in ["confirmed", "has confirmed", "tests confirmed"]):
            type_status = "Confirmed"
            now_taipei = datetime.now(timezone.utc) + timedelta(hours=8)
            confirm_date = now_taipei.strftime("%Y-%m-%d")
            notes_prefix = "官方已確診病例。"
            
        # 5. 建立新病例項目
        new_case = {
            "id": f"CASE-{case_idx:03d}",
            "type": type_status,
            "species": "野生候鳥 (野鳥監測)",
            "location": f"新偵測：{loc}",
            "latitude": lat,
            "longitude": lon,
            "found_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "notify_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "confirm_date": confirm_date,
            "notes": f"【動態爬蟲自動生成】{notes_prefix}來源文字段落：\"{src_txt}\""
        }
        print(f"[動態新增成功] 成功將新地點 '{loc}' 寫入病例資料庫 (ID: {new_case['id']}, 坐標: {lat}, {lon})")
        new_discovered.append(new_case)
        case_idx += 1
        
    return new_discovered

def fetch_daff_updates():
    """
    從澳洲農業部官網 (DAFF) 及 NSW DPIRD 官網爬取最新資訊，並對病例進行動態狀態比對與升級。
    """
    daff_url = "https://www.agriculture.gov.au/node/26086"
    nsw_url = "https://www.dpird.nsw.gov.au/dpi/biosecurity/animal-biosecurity/avian-influenza"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }
    
    daff_soup = None
    nsw_soup = None
    
    # 1. 爬取聯邦 DAFF 官網
    print(f"正在連線澳洲農業部官網: {daff_url} ...")
    try:
        response = requests.get(daff_url, headers=headers, timeout=20)
        if response.status_code == 200:
            daff_soup = BeautifulSoup(response.text, "html.parser")
        else:
            print(f"警告: 聯邦 DAFF 連線失敗，HTTP 狀態碼: {response.status_code}")
    except Exception as e:
        print(f"警告: 聯邦 DAFF 連線錯誤: {str(e)}")
        
    # 2. 爬取新南威爾斯州 DPIRD 官網
    print(f"正在連線新南威爾斯州 DPIRD 官網: {nsw_url} ...")
    try:
        response = requests.get(nsw_url, headers=headers, timeout=20)
        if response.status_code == 200:
            nsw_soup = BeautifulSoup(response.text, "html.parser")
        else:
            print(f"警告: NSW DPIRD 連線失敗，HTTP 狀態碼: {response.status_code}")
    except Exception as e:
        print(f"警告: NSW DPIRD 連線錯誤: {str(e)}")
        
    # 建立深層複製，避免影響預設資料
    cases = json.loads(json.dumps(DEFAULT_CASES))
    
    # 輔助比對函數：尋找特定地點名稱之段落是否包含「確診 (confirmed)」關鍵字
    def check_confirmed_in_soup(soup, location_keyword):
        if not soup:
            return False
        paragraphs = [p.text for p in soup.find_all(["p", "li"]) if location_keyword in p.text]
        for p in paragraphs:
            if any(kw in p.lower() for kw in ["confirmed", "has confirmed", "tests confirmed", "confirmed as"]):
                return True
        return False

    # 比對與升級規則 (1)：比對 Roses Beach 案例是否已經確診
    if check_confirmed_in_soup(daff_soup, "Roses Beach") or check_confirmed_in_soup(nsw_soup, "Roses Beach"):
        for case in cases:
            if case["id"] == "CASE-005":
                if case["type"] != "Confirmed":
                    case["type"] = "Confirmed"
                    now_taipei = datetime.now(timezone.utc) + timedelta(hours=8)
                    case["confirm_date"] = now_taipei.strftime("%Y-%m-%d")
                    case["notes"] = "原西澳 Roses Beach 疑似病例，經 ACDP 國家實驗室進一步檢測，官方已正式升級為確診病例。"
                    print("[動態更新] 偵測到 Roses Beach 疑似病例 (CASE-005) 已轉為『確診』狀態！")
                                
    # 比對與升級規則 (2)：比對 Hawks Nest 案例是否已經確診
    if check_confirmed_in_soup(daff_soup, "Hawks Nest") or check_confirmed_in_soup(nsw_soup, "Hawks Nest"):
        for case in cases:
            if case["id"] == "CASE-007":
                if case["type"] != "Confirmed":
                    case["type"] = "Confirmed"
                    now_taipei = datetime.now(timezone.utc) + timedelta(hours=8)
                    case["confirm_date"] = now_taipei.strftime("%Y-%m-%d")
                    case["notes"] = "新南威爾斯州 (NSW) 首宗確診病例。原 Hawks Nest 疑似病例，經 ACDP 國家實驗室檢測，官方已正式升級為確診病例。"
                    print("[動態更新] 偵測到 Hawks Nest 疑似病例 (CASE-007) 已轉為『確診』狀態！")
            
    # 3. 動態發現全新疫情地點並加入病例庫 (AI 智慧定位模組)
    discovered_cases = discover_new_cases(daff_soup, cases) + discover_new_cases(nsw_soup, cases)
    for nc in discovered_cases:
        # 坐報防重覆寫入 (10公里範圍內不重覆)
        if not any(abs(c["latitude"] - nc["latitude"]) + abs(c["longitude"] - nc["longitude"]) < 0.1 for c in cases):
            cases.append(nc)

    return cases

def generate_dynamic_summary(cases_data):
    """
    根據當前的病例數據，動態產生包含超連結與 current status 的官方事實與媒體觀察摘要。
    """
    # 1. 統計各州數據
    states_stats = {
        "WA": {"Confirmed": 0, "Suspect": 0, "Negative": 0, "total": 0},
        "SA": {"Confirmed": 0, "Suspect": 0, "Negative": 0, "total": 0},
        "NSW": {"Confirmed": 0, "Suspect": 0, "Negative": 0, "total": 0},
        "Other": {"Confirmed": 0, "Suspect": 0, "Negative": 0, "total": 0}
    }
    
    for case in cases_data:
        loc = case["location"]
        c_type = case["type"]
        
        # 判定屬於哪一州
        state_key = "Other"
        if "西澳" in loc or "WA" in loc or "Esperance" in loc or "Dunsborough" in loc or "Roses" in loc:
            state_key = "WA"
        elif "南澳" in loc or "SA" in loc or "Fleurieu" in loc or "Fowlers" in loc:
            state_key = "SA"
        elif "新南威爾斯" in loc or "NSW" in loc or "Hawks Nest" in loc:
            state_key = "NSW"
            
        states_stats[state_key][c_type] += 1
        states_stats[state_key]["total"] += 1

    # 2. 拼裝官方事實段落
    daff_link = '<a href="https://www.agriculture.gov.au/node/26086" target="_blank" class="text-blue-400 underline hover:text-blue-300 font-semibold">澳洲聯邦農業部 (DAFF)</a>'
    
    wa_detail = f"西澳 {states_stats['WA']['total']} 例（{states_stats['WA']['Confirmed']}例確診" + (f"/{states_stats['WA']['Suspect']}例疑似" if states_stats['WA']['Suspect'] else "") + ")"
    sa_detail = f"南澳 {states_stats['SA']['total']} 例（{states_stats['SA']['Confirmed']}例確診" + (f"/{states_stats['SA']['Negative']}例已排除" if states_stats['SA']['Negative'] else "") + ")"
    
    # 針對 NSW，我們特別顯示目前只有 1 例且是疑似
    nsw_detail = f"新南威爾斯州 (NSW) {states_stats['NSW']['total']} 例（"
    if states_stats['NSW']['Confirmed'] > 0:
        nsw_detail += f"{states_stats['NSW']['Confirmed']}例確診"
    else:
        nsw_detail += f"{states_stats['NSW']['Suspect']}例疑似"
    nsw_detail += ")"
    
    official_text = (
        f"依據 {daff_link} 及各州政府最新公告，目前全澳所有高致病性 H5N1 檢出均侷限於沿海地區之野生遷徙海鳥。當前最新疫情病例分布統計：{wa_detail}、{sa_detail}、以及{nsw_detail}。全澳家禽產業及商業飼料生產體系 100% 維持無疫區（Area Freedom）狀態，生產鏈安全無虞。"
    )

    # 3. 拼裝媒體觀察段落
    # 我們找出最新通報的一起病例（notify_date 最新的那筆，或者列表最後一筆）
    latest_case = cases_data[-1] if cases_data else None
    
    nsw_dpird_link = '<a href="https://www.dpird.nsw.gov.au/dpi/biosecurity/animal-biosecurity/avian-influenza" target="_blank" class="text-blue-400 underline hover:text-blue-300 font-semibold">新南威爾斯州政府 (NSW DPIRD)</a>'
    abc_link = '<a href="https://www.abc.net.au/news/" target="_blank" class="text-blue-400 underline hover:text-blue-300 font-semibold">澳洲廣播公司 (ABC News)</a>'
    
    media_text = ""
    if latest_case:
        loc_name = latest_case["location"].replace("新偵測：", "")
        species = latest_case["species"]
        if latest_case["type"] == "Suspect":
            media_text = (
                f"根據 {abc_link} 與 {nsw_dpird_link} 報導指出，最新於 {loc_name} 發現之 {species} 初步篩檢（快篩）呈現 H5 陽性，目前列為疑似病例，檢體已送往 CSIRO 國家實驗室 (ACDP) 進行最終確診覆檢。此零星野鳥病例並未對距離本廠 290 公里之內陸高地的 Blayney 廠生產造成任何威脅。"
            )
        else:
            media_text = (
                f"根據 {abc_link} 與 {nsw_dpird_link} 最新報導，{loc_name} 爆發之 {species} 疫情已正式被官方實驗室確認。地方政府已啟動緊急生物安全監控，目前無家禽受波及。本廠將持續維持與該地區地緣防線之安全監控。"
            )
    else:
        media_text = f"根據 {abc_link} 與 {nsw_dpird_link} 報導，目前澳洲野鳥疫情局勢尚無最新突破性變動，地方監控組織正密切維持常態性觀測。"
        
    return official_text, media_text

def main():
    # 1. 抓取最新病例數據
    cases_data = fetch_daff_updates()
    
    # 2. 依照「官方通報/採樣日期」由先至後進行排序 (Ascending Chronological Order)
    cases_data.sort(key=lambda x: x["notify_date"])
    
    # 3. 讀取網頁模板檔案 (report_template.html)
    template_path = "report_template.html"
    output_path = "index.html"
    
    if not os.path.exists(template_path):
        print(f"嚴重錯誤：找不到模板檔案 '{template_path}'，請確認模板是否存在儲存庫根目錄！")
        return
        
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()
    
    # 4. 根據最新病例數據動態產生官方事實與媒體觀察摘要
    official_html, media_html = generate_dynamic_summary(cases_data)
    updated_html = html_template.replace("<!-- DYNAMIC_OFFICIAL_SUMMARY_PLACEHOLDER -->", official_html)
    updated_html = updated_html.replace("<!-- DYNAMIC_MEDIA_SUMMARY_PLACEHOLDER -->", media_html)
    
    # 5. 將最新的病例數據 JSON 注入模板預留的佔位符中，並將模板中原有的預設 JavaScript 陣列完全替換
    cases_json_str = json.dumps(cases_data, ensure_ascii=False, indent=2)
    updated_html = re.sub(
        r'/\* CASES_DATABASE_PLACEHOLDER \*/\s*\[.*?\]\s*;', 
        f"/* CASES_DATABASE_PLACEHOLDER */ {cases_json_str};", 
        updated_html, 
        flags=re.DOTALL
    )
    
    # 6. 更新最後編譯更新時間 (校正為台北時間與澳洲 AEST 時間)
    utc_now = datetime.now(timezone.utc)
    taipei_now = utc_now + timedelta(hours=8)
    aest_now = utc_now + timedelta(hours=10)
    time_string = f"{taipei_now.strftime('%Y-%m-%d %H:%M:%S')} (台北時間) / {aest_now.strftime('%Y-%m-%d %H:%M:%S')} (澳洲 AEST)"
    updated_html = updated_html.replace("<!-- COMPILE_TIME_PLACEHOLDER -->", time_string)
    
    # 7. 寫出為正式部署網頁 index.html
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(updated_html)
        
    print(f"網頁自動編譯成功！已順利生成最新 H5N1 戰略決策報告 '{output_path}'。")

if __name__ == "__main__":
    main()
