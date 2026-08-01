import os
import requests
import json
import hashlib
import time
import base64
import re
import urllib3
import xml.etree.ElementTree as ET
from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# 設定與環境變數
TG_TOKEN = os.environ.get('TG_TOKEN')
TG_CHAT_ID = os.environ.get('TG_CHAT_ID')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
CF_WORKER_URL = os.environ.get('CF_WORKER_URL', 'https://round-recipe-c3ef.bluebird-finder-tw.workers.dev')
LOCAL_DEV = os.environ.get('LOCAL_DEV', 'false').lower() == 'true'

STATUS_FILE = "status.json"

# 繞過公司代理 SSL 驗證
if LOCAL_DEV:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 狀態追蹤函數 ---
def load_status():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"載入狀態檔案失敗: {e}")
    return {
        "notified_nz_newsletters": [],
        "notified_au_news": [],
        "notified_wahis_reports": [],
        "notified_aphia_articles": [],
        "usda_latest_date": "",
        "usda_total_birds_30d": "",
        "usda_confirmed_flocks_30d": 0
    }

def save_status(status):
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"儲存狀態檔案失敗: {e}")

# --- HTML 標籤清理函數 (確保符合 Telegram 限制) ---
def clean_telegram_html(text):
    if not text:
        return ""
    # 還原字面量的 \n 轉義反斜線為真正的換行符
    text = text.replace('\\n', '\n')
    text = re.sub(r'</?(p|h1|h2|h3|h4|h5|h6|div)[^>]*>', '\n', text)
    text = re.sub(r'<li>', '• ', text)
    text = re.sub(r'</li>', '\n', text)
    text = re.sub(r'</?(ul|ol)[^>]*>', '', text)
    text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    
    supported_tags = ['b', 'strong', 'i', 'em', 'u', 'ins', 's', 'strike', 'del', 'a', 'code', 'pre']
    
    def tag_repl(match):
        tag_content = match.group(0)
        is_closing = tag_content.startswith('</')
        tag_name_match = re.match(r'</?([a-zA-Z0-9]+)', tag_content)
        if tag_name_match:
            tag_name = tag_name_match.group(1).lower()
            if tag_name in supported_tags:
                if tag_name == 'a' and not is_closing:
                    href_match = re.search(r'href=["\']([^"\']+)["\']', tag_content)
                    if href_match:
                        return f'<a href="{href_match.group(1)}">'
                    return '<a>'
                return f'</{tag_name}>' if is_closing else f'<{tag_name}>'
        return ""
        
    text = re.sub(r'</?[a-zA-Z0-9]+[^>]*>', tag_repl, text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text.strip()

# --- Telegram 發送函數 ---
def send_telegram_message(text):
    print("正在發送 Telegram 文字訊息...")
    text = clean_telegram_html(text)
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "link_preview_options": {"is_disabled": True}
    }
    verify_ssl = not LOCAL_DEV
    try:
        res = requests.post(url, json=payload, verify=verify_ssl)
        if res.status_code == 200:
            print("Telegram 文字訊息發送成功。")
        else:
            print(f"Telegram 文字訊息發送失敗，狀態碼: {res.status_code}，回應: {res.text}")
    except Exception as e:
        print(f"無法發送 Telegram 訊息: {e}")

def send_telegram_photo(photo_path, caption):
    print("正在發送 Telegram 照片...")
    caption = clean_telegram_html(caption)
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
    verify_ssl = not LOCAL_DEV
    try:
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': TG_CHAT_ID,
                'caption': caption,
                'parse_mode': 'HTML'
            }
            res = requests.post(url, data=data, files=files, verify=verify_ssl)
            if res.status_code == 200:
                print("Telegram 照片發送成功。")
            else:
                print(f"Telegram 照片發送失敗，狀態碼: {res.status_code}，回應: {res.text}")
    except Exception as e:
        print(f"無法發送 Telegram 照片: {e}")

# --- Gemini API 輔助安全性設定 ---
def get_safety_settings():
    return [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]

# --- 集中管理 Gemini API 呼叫 (含 429 自動重試機制) ---
def call_gemini_api(url, payload):
    verify_ssl = not LOCAL_DEV
    for attempt in range(3):
        try:
            res = requests.post(url, json=payload, verify=verify_ssl)
            if res.status_code == 429:
                print(f"收到 Gemini API 429 (Too Many Requests)，等待 30 秒後重試 (第 {attempt+1} 次)...")
                time.sleep(30)
                continue
            res.raise_for_status()
            
            # 成功取得回應後，強制 sleep 15 秒以拉開與下一次請求的間隔，保護 Rate Limit
            print("Gemini API 請求成功。等待 15 秒以拉開與下一模組的請求間隔...")
            time.sleep(15)
            
            return res.json()
        except Exception as e:
            if attempt < 2:
                print(f"呼叫 Gemini API 發生錯誤: {e}，等待 10 秒後重試...")
                time.sleep(10)
            else:
                raise e
    raise Exception("呼叫 Gemini API 失敗，已達最大重試次數。")

# --- Gemini API 函數 ---
def get_ai_summary(name, content):
    print(f"正在向 Gemini 請求 {name} 的文字摘要...")
    prompt = (
        f"您是一位生物安全專家。請分析這份來自 {name} 的資料。\n"
        "請重點摘要以下疫情細節：日期、地點（州/郡或國家）、受影響的場數/類型、鳥隻或動物數量。\n"
        "特別留意是否有提到因為澳洲最近的疫情讓紐西蘭政府有所警覺或調整防範措施。\n"
        "請使用繁體中文（台灣用語）提供結構化摘要。格式請「僅使用」以下 Telegram 支援的 HTML 標籤：\n"
        "<b>, <i>, <u>, <s>, <a href=\"...\">, <code>, <pre>。\n"
        "請絕對「不能使用」 <br>, <p>, <h1>, <h2>, <h3>, <ul>, <li>, <div> 等不支援的標籤！\n"
        "換行請直接使用標準換行字元 (\\n)，列表項目請直接在行首使用 '-' 或 '•' 字符來代表。"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{prompt}\n\nContent:\n{content[:15000]}"}
                ]
            }
        ],
        "safetySettings": get_safety_settings()
    }
    
    try:
        res_json = call_gemini_api(url, payload)
        candidates = res_json.get('candidates', [])
        if not candidates:
            print("Gemini API 未傳回任何候選結果，完整回應：", res_json)
            return "無法生成摘要：API 未傳回結果。"
            
        candidate = candidates[0]
        content_obj = candidate.get('content', {})
        parts = content_obj.get('parts', [])
        if not parts:
            finish_reason = candidate.get('finishReason', 'UNKNOWN')
            print(f"Gemini API 回傳內容為空，結束原因: {finish_reason}。完整回應：", res_json)
            return f"無法生成摘要（API 結束原因: {finish_reason}）。"
            
        return parts[0].get('text', '')
    except Exception as e:
        print(f"呼叫 Gemini 摘要時發生錯誤: {e}")
        return "無法生成摘要（API 呼叫失敗）。"

def get_ai_vision_summary(image_path):
    print("正在向 Gemini 請求看板截圖視覺分析...")
    with open(image_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
        
    prompt = (
        "您是一位生物安全專家。請分析這張美國 USDA 禽流感（HPAI）統計數據看板的截圖。\n"
        "請返回一個 JSON 物件，包含以下四個欄位（欄位名稱請務必精確相符）：\n"
        "1. \"summary_html\": 繁體中文（台灣用語）排版的疫情敘述。包含最近 30 天的統計摘要（確診場數、商業/家庭養殖場分佈、受影響鳥隻總數），以及從下方的「List of Detections by Day」表格中，列出最新的幾筆疫情案例細節，包含確診日期（如 23-Jun-26 需寫為 2026年6月23日）、州別、郡別、養殖場類型（如 WOAH Poultry/WOAH Non-Poultry等）、受影響數量。\n"
        "格式請「僅使用」以下 Telegram 支援的 HTML 標籤： <b>, <i>, <u>, <s>, <a href=\"...\">, <code>, <pre>。\n"
        "請絕對「不能使用」 <br>, <p>, <h1>, <h2>, <h3>, <ul>, <li>, <div> 等不支援的標籤！\n"
        "換行請直接使用標準換行字元 (\\n)，列表項目請直接在行首使用 '-' 或 '•' 字符來代表。\n"
        "2. \"latest_detection_date\": 看板中最新的確診日期（格式如 \"2026-06-23\"）。\n"
        "3. \"total_birds_30d\": 最近 30 天受影響的鳥隻總數（例如 \"0.10M\" 或 \"100,000\"）。\n"
        "4. \"confirmed_flocks_30d\": 最近 30 天確診的場數（必須是整數，例如 12）。"
    )
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": img_base64
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        },
        "safetySettings": get_safety_settings()
    }
    
    res_json = call_gemini_api(url, payload)
    result_text = res_json['candidates'][0]['content']['parts'][0]['text']
    return json.loads(result_text)

def get_au_news_summary(content):
    print("正在向 Gemini 請求澳洲疫情新聞專業分析...")
    prompt = (
        "您是一位生物安全專家。請分析這篇關於澳洲禽流感（Avian Influenza / Bird Flu）的新聞報導文字。\n"
        "請用繁體中文（台灣用語）提供結構化摘要，並包含以下關鍵資訊：\n"
        "1. <b>確診地點與新南威爾斯州（NSW）風險評估</b>：說明本次疫情發生在澳洲哪裡。請**「特別以加粗字體」**評估並指出此病例對位於新南威爾斯州（NSW）的工廠是否有潛在風險（例如：若疫情已傳播至 NSW，必須強烈加粗警告可能影響出口台灣的資格；若發生在其他州如 SA 或 WA，也請說明目前是否與 NSW 隔絕）。\n"
        "2. <b>病毒株種類</b>：例如是 H5N1（高病原性）、H7 還是其他病毒株類型。\n"
        "3. <b>疫情嚴重度與受影響規模</b>：指明受影響的是野鳥、商業養殖場還是家庭養殖場，以及受影響的鳥隻或農場數量。\n"
        "4. <b>澳洲政府/防檢疫單位的因應措施</b>：例如劃定管制區、撲殺、提高監控警戒等。\n\n"
        "格式要求：請「僅使用」以下 Telegram 支援的 HTML 標籤：<b>, <i>, <u>, <s>, <a href=\"...\">, <code>, <pre>。\n"
        "絕對「不能使用」 <br>, <p>, <h1>, <h2>, <h3>, <ul>, <li>, <div> 等標籤！\n"
        "換行請直接使用標準換行字元 (\\n)，列表項目請直接在行首使用 '-' 或 '•' 字符來代表。"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{prompt}\n\nContent:\n{content[:15000]}"}
                ]
            }
        ],
        "safetySettings": get_safety_settings()
    }
    
    try:
        res_json = call_gemini_api(url, payload)
        candidates = res_json.get('candidates', [])
        if not candidates:
            print("Gemini API 未傳回任何候選結果，完整回應：", res_json)
            return "無法生成摘要：API 未傳回結果。"
            
        candidate = candidates[0]
        content_obj = candidate.get('content', {})
        parts = content_obj.get('parts', [])
        if not parts:
            finish_reason = candidate.get('finishReason', 'UNKNOWN')
            print(f"Gemini API 回傳內容為空，結束原因: {finish_reason}。完整回應：", res_json)
            return f"無法生成摘要（API 結束原因: {finish_reason}）。"
            
        return parts[0].get('text', '')
    except Exception as e:
        print(f"呼叫 Gemini 摘要時發生錯誤: {e}")
        return "無法生成摘要（API 呼叫失敗）。"

def get_wahis_summary(item):
    print(f"正在向 Gemini 請求 WOAH Report {item.get('reportId')} 的摘要...")
    prompt = (
        "您是一位生物安全專家。請根據以下 WOAH WAHIS 疫情通報數據寫一段簡短的繁體中文（台灣用語）摘要。\n"
        "重點解釋：此通報的國家、病原體（病毒株）、通報原因，並評估這對於國際貿易及台灣進口限制的潛在影響（特別注意：如果事件發生在澳洲或紐西蘭，請說明對該國以及新南威爾斯州 NSW 寵物食品出口的潛在警訊）。\n"
        "格式請「僅使用」以下 Telegram 支援的 HTML 標籤：<b>, <i>, <u>, <s>, <a href=\"...\">, <code>, <pre>。\n"
        "絕對「不能使用」 <br>, <p>, <h1>, <h2>, <h3>, <ul>, <li>, <div> 等不支援的標籤！\n"
        "換行請直接使用標準換行字元 (\\n)，列表項目請直接在行首使用 '-' 或 '•' 字符來代表。"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{prompt}\n\nData:\n{json.dumps(item, ensure_ascii=False)}"}
                ]
            }
        ],
        "safetySettings": get_safety_settings()
    }
    
    try:
        res_json = call_gemini_api(url, payload)
        candidates = res_json.get('candidates', [])
        if not candidates:
            print("Gemini API 未傳回任何候選結果，完整回應：", res_json)
            return "無法生成摘要：API 未傳回結果。"
            
        candidate = candidates[0]
        content_obj = candidate.get('content', {})
        parts = content_obj.get('parts', [])
        if not parts:
            finish_reason = candidate.get('finishReason', 'UNKNOWN')
            print(f"Gemini API 回傳內容為空，結束原因: {finish_reason}。完整回應：", res_json)
            return f"無法生成摘要（API 結束原因: {finish_reason}）。"
            
        return parts[0].get('text', '')
    except Exception as e:
        print(f"呼叫 Gemini 摘要時發生錯誤: {e}")
        return "無法生成摘要（API 呼叫失敗）。"

# --- 日期解析與時間過濾輔助函數 ---
def parse_nz_date(date_str):
    date_str = date_str.strip()
    for fmt in ("%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    for fmt in ("%d %B", "%d %b"):
        try:
            dt = datetime.strptime(date_str, fmt)
            now = datetime.now()
            dt = dt.replace(year=now.year)
            if dt > now:
                dt = dt.replace(year=now.year - 1)
            return dt
        except ValueError:
            continue
    return None

def parse_rss_date(date_str):
    date_str = date_str.strip()
    cleaned_str = re.sub(r'\s*(GMT|[+-]\d{4})$', '', date_str)
    try:
        return datetime.strptime(cleaned_str, "%a, %d %b %Y %H:%M:%S")
    except Exception as e:
        print(f"無法解析 RSS 日期 {date_str}: {e}")
    return None

def parse_iso_date(date_str):
    # e.g., "2026-06-20T07:56:35.861+00:00"
    date_str = date_str.strip()
    cleaned_str = re.sub(r'([+-]\d{2}):(\d{2})$', r'\1\2', date_str)
    cleaned_str = cleaned_str.replace("Z", "+0000")
    cleaned_str = re.sub(r'\.\d+', '', cleaned_str)
    try:
        return datetime.strptime(cleaned_str, "%Y-%m-%dT%H:%M:%S%z")
    except Exception as e:
        try:
            naive_str = re.sub(r'T', ' ', cleaned_str[:19])
            return datetime.strptime(naive_str, "%Y-%m-%d %H:%M:%S")
        except Exception as ex:
            print(f"無法解析 ISO 日期 {date_str}: {ex}")
    return None

# --- 主要執行流程 ---
def run():
    status = load_status()
    updated = False
    
    print("啟動 Playwright 瀏覽器 (含擬真隱身與反爬蟲設定)...")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-http2", "--no-sandbox"])
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            ignore_https_errors=LOCAL_DEV,
            user_agent=user_agent,
            locale="en-US"
        )
        page = context.new_page()
        # 抹去 Playwright 自動化特徵 navigator.webdriver
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # ==========================================
        # 1. 🇹🇼 台灣防檢署 (APHIA) 疫區公告監控
        # ==========================================
        try:
            print("正在獲取台灣防檢署疫區公告列表...")
            aphia_pages = [
                "https://www.aphia.gov.tw/ws.php?id=17437",  # 歷史列表
                "https://www.aphia.gov.tw/ws.php?id=17438",  # 最新公告
            ]
            verify_ssl = not LOCAL_DEV
            seen_article_urls = set()
            all_article_links_data = []
            
            for aphia_url in aphia_pages:
                try:
                    res = requests.get(aphia_url, verify=verify_ssl, timeout=30)
                    res.encoding = 'utf-8'
                    if res.status_code == 200:
                        page_soup = BeautifulSoup(res.text, 'html.parser')
                        page_links = page_soup.find_all('a', class_='lists')
                        print(f"從 {aphia_url} 找到 {len(page_links)} 則公告。")
                        for lt in page_links:
                            href = lt.get('href', '')
                            if href:
                                full_url = f"https://www.aphia.gov.tw/{href}"
                                if full_url not in seen_article_urls:
                                    seen_article_urls.add(full_url)
                                    all_article_links_data.append((lt, full_url))
                except Exception as page_err:
                    print(f"抓取 {aphia_url} 失敗: {page_err}")
            
            print(f"防檢署公告合併去重後共 {len(all_article_links_data)} 則。")
            
            if all_article_links_data:
                is_first_run = len(status.get("notified_aphia_articles", [])) == 0
                candidates = []
                
                for link_tag, article_url in all_article_links_data:
                    if article_url in status.get("notified_aphia_articles", []):
                        continue
                    
                    date_div = link_tag.find(class_='data')
                    title_div = link_tag.find(class_='h3')
                    date_str = date_div.get_text(strip=True) if date_div else ''
                    title_text = title_div.get_text(strip=True) if title_div else link_tag.get_text(strip=True)
                    
                    dt = None
                    if date_str:
                        try:
                            dt = datetime.strptime(date_str, "%Y-%m-%d")
                        except Exception:
                            pass
                    
                    if not dt:
                        continue
                    
                    if is_first_run:
                        is_in_window = (dt.year == datetime.now().year)
                    else:
                        is_in_window = (datetime.now() - dt).days <= 7
                    
                    if is_in_window:
                        candidates.append({
                            "url": article_url,
                            "date_str": date_str,
                            "title": title_text,
                            "date_dt": dt
                        })
                
                candidates.sort(key=lambda x: x["date_dt"], reverse=True)
                print(f"符合發送條件的全新防檢署公告數量: {len(candidates)}")
                
                if candidates:
                    target = candidates[0]
                    a_url = target["url"]
                    a_date = target["date_str"]
                    a_title = target["title"]
                    
                    print(f"發現符合條件的全新防檢署公告，發送最新的一筆：{a_date} - {a_title[:50]}")
                    
                    article_res = requests.get(a_url, verify=verify_ssl, timeout=30)
                    article_res.encoding = 'utf-8'
                    article_soup = BeautifulSoup(article_res.text, 'html.parser')
                    
                    article_text = ""
                    for cls in ['newsp', 'newsdeTitle', 'nlist']:
                        elem = article_soup.find(class_=cls)
                        if elem:
                            article_text += elem.get_text(separator='\n', strip=True) + '\n\n'
                    
                    if not article_text.strip():
                        article_text = article_soup.get_text(separator='\n', strip=True)[:5000]
                    
                    summary = get_ai_summary("台灣農業部動植物防疫檢疫署 (APHIA) 疫區公告", article_text)
                    
                    message = (
                        f"🇹🇼 <b>台灣防檢署疫區公告更新 ({a_date})</b>\n"
                        f"公告標題：{a_title}\n"
                        f"公告連結：<a href='{a_url}'>閱讀原文</a>\n\n"
                        f"{summary}"
                    )
                    
                    send_telegram_message(message)
                    
                    if "notified_aphia_articles" not in status:
                        status["notified_aphia_articles"] = []
                    for cand in candidates:
                        if cand["url"] not in status["notified_aphia_articles"]:
                            status["notified_aphia_articles"].append(cand["url"])
                    updated = True
                else:
                    print("防檢署疫區公告無更新，跳過。")
            else:
                print("防檢署公告列表抓取失敗，無任何資料。")
                
        except Exception as e:
            print(f"檢查台灣防檢署 APHIA 失敗: {e}")

        # ==========================================
        # 2. 🇺🇸 美國 USDA 看板監控
        # ==========================================
        try:
            print("正在前往美國 USDA HPAI 網頁...")
            page.goto("https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections/commercial-backyard-flocks", wait_until="domcontentloaded", timeout=90000)
            
            print("等待 Tableau 儀表板載入...")
            page.wait_for_selector(".c-iframe-embed iframe", timeout=30000)
            time.sleep(15)
            
            screenshot_path = "usda_tableau.png"
            iframe_element = page.locator(".c-iframe-embed iframe")
            iframe_element.screenshot(path=screenshot_path)
            print(f"已儲存元素截圖至 {screenshot_path}")
            
            vision_data = get_ai_vision_summary(screenshot_path)
            
            latest_date = vision_data.get("latest_detection_date", "")
            total_birds = vision_data.get("total_birds_30d", "")
            confirmed_flocks = vision_data.get("confirmed_flocks_30d", 0)
            summary_html = vision_data.get("summary_html", "")
            
            print(f"USDA 最新數據：日期={latest_date}, 鳥隻數={total_birds}, 場數={confirmed_flocks}")
            
            latest_date_dt = None
            if latest_date:
                try:
                    latest_date_dt = datetime.strptime(latest_date, "%Y-%m-%d")
                except Exception as ex:
                    print(f"解析 USDA 最新日期失敗: {ex}")
            
            is_first_run = not status.get("usda_latest_date")
            is_recent = True
            if latest_date_dt:
                is_recent = (datetime.now() - latest_date_dt).days <= 7
                
            has_changed = (latest_date != status.get("usda_latest_date") or 
                           total_birds != status.get("usda_total_birds_30d") or 
                           confirmed_flocks != status.get("usda_confirmed_flocks_30d"))
            
            if has_changed:
                if is_first_run or is_recent:
                    caption = (
                        f"🇺🇸 <b>美國 USDA HPAI 統計數據看板更新</b>\n"
                        f"資料來源：<a href='https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections/commercial-backyard-flocks'>USDA APHIS</a>\n\n"
                        f"{summary_html}"
                    )
                    send_telegram_photo(screenshot_path, caption)
                else:
                    print(f"USDA 看板有更新但最新日期 ({latest_date}) 超過 7 天且非首次執行，跳過發送。")
                
                status["usda_latest_date"] = latest_date
                status["usda_total_birds_30d"] = total_birds
                status["usda_confirmed_flocks_30d"] = confirmed_flocks
                updated = True
            else:
                print("USDA 看板數據無更新，跳過發送。")
                
        except Exception as e:
            print(f"檢查 USDA 失敗: {e}")

        # ==========================================
        # 3. 🇦🇺 澳洲禽流感新聞監控 (含擬真過濾與自動 Failover)
        # ==========================================
        try:
            print("正在獲取 Google News 澳洲禽流感 RSS 訂閱源...")
            rss_url = "https://news.google.com/rss/search?q=%28%22avian+influenza%22+OR+%22bird+flu%22+OR+%22HPAI%22+OR+%22H5N1%22+OR+%22H7N9%22+OR+%22H5N2%22+OR+%22H5N8%22+OR+%22H7N3%22+OR+%22H7N7%22+OR+%22H7N8%22+OR+%22H5%22+OR+%22H7%22%29+australia&hl=en-AU&gl=AU"
            verify_ssl = not LOCAL_DEV
            headers = {'User-Agent': user_agent}
            res = requests.get(rss_url, verify=verify_ssl, headers=headers, timeout=30)
            
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                items = root.findall(".//item")
                print(f"在 RSS 中找到 {len(items)} 則新聞。")
                
                is_first_run = len(status.get("notified_au_news", [])) == 0
                candidates = []
                
                for item in items:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pub_date_elem = item.find('pubDate')
                    desc_elem = item.find('description')
                    
                    title = title_elem.text if title_elem is not None else ""
                    link = link_elem.text if link_elem is not None else ""
                    pub_date_str = pub_date_elem.text if pub_date_elem is not None else ""
                    description = desc_elem.text if desc_elem is not None else ""
                    
                    if not link or link in status.get("notified_au_news", []):
                        continue
                        
                    dt = parse_rss_date(pub_date_str)
                    if not dt:
                        continue
                        
                    if is_first_run:
                        is_in_window = (dt.year == datetime.now().year)
                    else:
                        is_in_window = (datetime.now() - dt).days <= 7
                        
                    if is_in_window:
                        candidates.append({
                            "title": title,
                            "link": link,
                            "pub_date": pub_date_str,
                            "date_dt": dt,
                            "description": description
                        })
                
                PRIORITY_DOMAINS = [".gov.au", "wildlifehealthaustralia.com.au", "abc.net.au", "9news.com.au"]
                
                def get_sort_key(cand):
                    is_official = any(dom in cand["link"].lower() for dom in PRIORITY_DOMAINS)
                    official_key = 0 if is_official else 1
                    time_key = -cand["date_dt"].timestamp()
                    return (official_key, time_key)
                
                candidates.sort(key=get_sort_key)
                print(f"符合發送條件的全新新聞數量: {len(candidates)}")
                
                sent_success = False
                blocked_keywords = ["bot detection", "robot", "captcha", "access denied", "pardon our interruption", "enable javascript", "news corp australia", "verify you are human", "subscribe to read"]
                
                for target_news in candidates:
                    n_link = target_news["link"]
                    n_title = target_news["title"]
                    n_date = target_news["pub_date"]
                    
                    print(f"嘗試抓取澳洲新聞: {n_title} ({n_link})...")
                    news_text = ""
                    dest_title = n_title
                    
                    # 嘗試通道 1：優先透過 Cloudflare Worker 代理轉發
                    if CF_WORKER_URL:
                        try:
                            from urllib.parse import quote
                            proxy_endpoint = f"{CF_WORKER_URL.rstrip('/')}/?url={quote(n_link, safe='')}"
                            print(f"透過 Cloudflare Worker 代理發送請求...")
                            w_res = requests.get(proxy_endpoint, headers=headers, timeout=20, verify=not LOCAL_DEV)
                            if w_res.status_code == 200 and w_res.text:
                                w_soup = BeautifulSoup(w_res.text, 'html.parser')
                                for s in w_soup(["script", "style"]):
                                    s.decompose()
                                extracted_text = w_soup.get_text(separator="\n", strip=True)
                                if extracted_text and len(extracted_text) >= 150:
                                    low_text = extracted_text.lower()
                                    if not any(kw in low_text for kw in blocked_keywords):
                                        news_text = extracted_text
                                        if w_soup.title and w_soup.title.string:
                                            dest_title = w_soup.title.string.strip()
                                        print("✅ 成功透過 Cloudflare Worker 代理取得乾淨新聞內文！")
                        except Exception as cf_err:
                            print(f"Cloudflare Worker 代理存取提示: {cf_err}")
                    
                    # 嘗試通道 2：若代理未取得，使用 Playwright Stealth 擬真瀏覽器
                    if not news_text:
                        try:
                            page.goto(n_link, wait_until="domcontentloaded", timeout=30000)
                            # 模擬人類行為：移動與滾動
                            page.mouse.move(100, 200)
                            page.evaluate("window.scrollBy(0, 300)")
                            time.sleep(3)
                            dest_title = page.title() or n_title
                            news_text = page.evaluate("() => document.body.innerText")
                        except Exception as page_err:
                            print(f"Playwright 載入頁面失敗: {page_err}")
                        
                    is_blocked = False
                    if not news_text or len(news_text.strip()) < 150:
                        is_blocked = True
                    else:
                        low_text = news_text.lower()
                        if any(kw in low_text for kw in blocked_keywords):
                            is_blocked = True
                            
                    if is_blocked:
                        print(f"⚠️ 澳洲新聞頁面遭反爬蟲阻擋或無效內容，跳過此則，標記已處理並嘗試下一則...")
                        if "notified_au_news" not in status:
                            status["notified_au_news"] = []
                        status["notified_au_news"].append(n_link)
                        continue
                        
                    summary = get_au_news_summary(news_text)
                    
                    invalid_summary_kw = ["無法提供", "非一篇關於", "機器人偵測", "阻擋通知"]
                    if any(ikw in summary for ikw in invalid_summary_kw):
                        print(f"⚠️ AI 摘要結果包含阻擋錯誤提示，標記已處理並嘗試下一則...")
                        if "notified_au_news" not in status:
                            status["notified_au_news"] = []
                        status["notified_au_news"].append(n_link)
                        continue
                        
                    message = (
                        f"🇦🇺 <b>澳洲禽流感最新疫情快報</b>\n"
                        f"新聞來源：<a href='{n_link}'>{dest_title}</a>\n"
                        f"發布時間：{n_date}\n\n"
                        f"{summary}"
                    )
                    
                    send_telegram_message(message)
                    sent_success = True
                    break
                
                # 若候選新聞全文皆被硬性阻擋，啟動 RSS 引文 (Snippet) 備援發送
                if not sent_success and candidates:
                    fallback_target = candidates[0]
                    fb_link = fallback_target["link"]
                    fb_title = fallback_target["title"]
                    fb_date = fallback_target["pub_date"]
                    fb_desc = BeautifulSoup(fallback_target["description"], "html.parser").get_text()
                    
                    print("啟用 RSS 引文 (Snippet) Fallback 進行分析發送...")
                    summary = get_au_news_summary(f"Title: {fb_title}\nSnippet: {fb_desc}")
                    
                    if not any(ikw in summary for ikw in ["無法提供", "非一篇關於", "機器人偵測"]):
                        message = (
                            f"🇦🇺 <b>澳洲禽流感最新疫情快報</b>\n"
                            f"新聞來源：<a href='{fb_link}'>{fb_title}</a>\n"
                            f"發布時間：{fb_date}\n\n"
                            f"{summary}"
                        )
                        send_telegram_message(message)
                
                if "notified_au_news" not in status:
                    status["notified_au_news"] = []
                for cand in candidates:
                    if cand["link"] not in status["notified_au_news"]:
                        status["notified_au_news"].append(cand["link"])
                if candidates:
                    updated = True
            else:
                print(f"獲取澳洲 RSS 失敗，狀態碼: {res.status_code}")
                
        except Exception as e:
            print(f"檢查澳洲新聞失敗: {e}")

        # ==========================================
        # 4. 🇳🇿 紐西蘭 MPI 電子報監控 (已更新 URL 與解析邏輯)
        # ==========================================
        try:
            print("正在前往紐西蘭 MPI 最新資源網頁...")
            nz_url = "https://www.mpi.govt.nz/biosecurity/pest-and-disease-threats-to-new-zealand/animal-disease-threats-to-new-zealand/bird-flu/bird-flu-newsletters-fact-sheets-science-reports-and-other-resources"
            
            page.goto(nz_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)
            
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            newsletter_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.get_text(strip=True)
                if any(domain in href for domain in ["createsend.com", "createsend1.com", "cmail20.com", "cmail"]):
                    newsletter_links.append({"date_text": text, "url": href})
            
            is_first_run = len(status.get("notified_nz_newsletters", [])) == 0
            candidates = []
            
            for item in newsletter_links:
                n_url = item["url"]
                n_date_text = item["date_text"]
                
                if n_url in status.get("notified_nz_newsletters", []):
                    continue
                    
                dt = parse_nz_date(n_date_text)
                if not dt:
                    continue
                    
                if is_first_run:
                    is_in_window = (dt.year == datetime.now().year)
                else:
                    is_in_window = (datetime.now() - dt).days <= 7
                    
                if is_in_window:
                    candidates.append({
                        "url": n_url,
                        "date_text": n_date_text,
                        "date_dt": dt
                    })
            
            candidates.sort(key=lambda x: x["date_dt"], reverse=True)
            print(f"符合發送條件的全新紐西蘭電子報數量: {len(candidates)}")
            
            if candidates:
                target = candidates[0]
                n_url = target["url"]
                n_date = target["date_text"]
                
                print(f"發現符合條件的全新電子報，發送最新的一筆：{n_date} ({n_url})")
                
                verify_ssl = not LOCAL_DEV
                res = requests.get(n_url, verify=verify_ssl, headers={'User-Agent': user_agent}, timeout=30)
                nsoup = BeautifulSoup(res.text, 'html.parser')
                newsletter_text = nsoup.get_text(separator="\n", strip=True)
                
                summary = get_ai_summary("紐西蘭 MPI 最新 HPAI 電子報", newsletter_text)
                
                message = (
                    f"🇳🇿 <b>紐西蘭 MPI / PIANZ 禽流感電子報摘要 ({n_date})</b>\n"
                    f"電子報連結：<a href='{n_url}'>閱讀原文</a>\n\n"
                    f"{summary}"
                )
                
                send_telegram_message(message)
                
                if "notified_nz_newsletters" not in status:
                    status["notified_nz_newsletters"] = []
                for cand in candidates:
                    if cand["url"] not in status["notified_nz_newsletters"]:
                        status["notified_nz_newsletters"].append(cand["url"])
                updated = True
            else:
                print("紐西蘭電子報無更新，跳過。")
                
        except Exception as e:
            print(f"檢查紐西蘭 MPI 失敗: {e}")

        # ==========================================
        # 5. 🌍 WOAH WAHIS 疫情通報監控
        # ==========================================
        try:
            print("正在獲取 WOAH WAHIS 疫情通報...")
            url = "https://wahis.woah.org/api/v1/pi/event/filtered-list?language=en"
            payload = {
                "eventIds": [], "reportIds": [], "countries": [15, 174, 239],
                "firstDiseases": [668, 671], "secondDiseases": [], "typeStatuses": [],
                "reasons": [], "eventStatuses": [], "reportTypes": [], "reportStatuses": [],
                "eventStartDate": None, "submissionDate": None, "animalTypes": [],
                "sortColumn": "submissionDate", "sortOrder": "desc", "pageSize": 10, "pageNumber": 0
            }
            verify_ssl = not LOCAL_DEV
            res = requests.post(url, json=payload, verify=verify_ssl, headers={'User-Agent': user_agent}, timeout=30)
            
            if res.status_code == 200:
                reports = res.json().get("list", [])
                print(f"在 WAHIS 中找到 {len(reports)} 則符合條件的通報。")
                
                is_first_run = len(status.get("notified_wahis_reports", [])) == 0
                candidates = []
                
                for item in reports:
                    r_id = item.get("reportId")
                    sub_date = item.get("submissionDate", "")
                    
                    if not r_id or r_id in status.get("notified_wahis_reports", []):
                        continue
                        
                    dt = parse_iso_date(sub_date)
                    if not dt:
                        continue
                        
                    naive_dt = dt.replace(tzinfo=None)
                    if is_first_run:
                        is_in_window = (naive_dt.year == datetime.now().year)
                    else:
                        is_in_window = (datetime.now() - naive_dt).days <= 7
                        
                    if is_in_window:
                        candidates.append({
                            "reportId": r_id,
                            "submissionDate": sub_date,
                            "date_dt": naive_dt,
                            "data": item
                        })
                
                candidates.sort(key=lambda x: x["date_dt"], reverse=True)
                print(f"符合發送條件的全新 WOAH 通報數量: {len(candidates)}")
                
                if candidates:
                    target_report = candidates[0]["data"]
                    r_id = target_report["reportId"]
                    
                    summary = get_wahis_summary(target_report)
                    
                    message = (
                        f"🌍 <b>WOAH WAHIS 疫情通報更新</b>\n"
                        f"國家：{target_report.get('country')}\n"
                        f"疾病名稱：{target_report.get('disease')}\n"
                        f"病毒亞型：<b>{target_report.get('subType')}</b>\n"
                        f"通報類型：{target_report.get('reportType')} (第 {target_report.get('reportNumber')} 報)\n"
                        f"通報原因：{target_report.get('reason')}\n"
                        f"提交日期：{target_report.get('submissionDate')[:10]}\n\n"
                        f"<b>專家摘要分析：</b>\n"
                        f"{summary}\n\n"
                        f"詳細報告連結：<a href='https://wahis.woah.org/#/report-details?reportId={r_id}'>檢視 WOAH 官方報告</a>"
                    )
                    
                    send_telegram_message(message)
                    
                    if "notified_wahis_reports" not in status:
                        status["notified_wahis_reports"] = []
                    for cand in candidates:
                        rc_id = cand["reportId"]
                        if rc_id not in status["notified_wahis_reports"]:
                            status["notified_wahis_reports"].append(rc_id)
                    updated = True
                else:
                    print("沒有符合發送條件的 WOAH 疫情通報更新。")
            else:
                print(f"獲取 WAHIS 失敗，狀態碼: {res.status_code}")
                
        except Exception as e:
            print(f"檢查 WOAH 失敗: {e}")
            
        browser.close()
        
    if updated:
        save_status(status)

if __name__ == "__main__":
    run()
