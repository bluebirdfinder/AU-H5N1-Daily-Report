import os
import requests
import json
import hashlib
from playwright.sync_api import sync_playwright

# 從 GitHub Secrets 讀取設定
TG_TOKEN = os.environ.get('TG_TOKEN')
TG_CHAT_ID = os.environ.get('TG_CHAT_ID')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

TARGETS = [
    {"name": "USA (Full Detection Table)", "url": "https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections/commercial-backyard-flocks", "type": "tableau"},
    {"name": "WOAH (Global Events)", "url": "https://wahis.woah.org/#/event-management", "type": "dynamic"},
    {"name": "NSW (Australia)", "url": "https://www.dpi.nsw.gov.au/dpi/biosecurity/animal-biosecurity/avian-influenza", "type": "static"}
]

def get_ai_summary(name, content):
    print(f"Requesting AI summary for {name}...")
    prompt = f"You are a biosecurity expert. Analyze this content from {name}. Highlight specific outbreak details: Date, Location (State/County), and Flock Size/Type. Provide summaries in Traditional Chinese and English."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": f"{prompt}\n\nContent:\n{content[:10000]}"}]}]}
    res = requests.post(url, json=payload)
    return res.json()['candidates'][0]['content']['parts'][0]['text']

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TG_CHAT_ID, "text": text})

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for target in TARGETS:
            try:
                print(f"Checking {target['name']}...")
                page.goto(target['url'], timeout=60000)
                
                if target['type'] == 'tableau':
                    page.wait_for_timeout(10000) # 等待畫布載入
                elif target['type'] == 'dynamic':
                    page.wait_for_load_state('networkidle')
                
                content = page.content()
                text_content = page.evaluate("() => document.body.innerText")
                
                # 此處可加入 Hash 比對邏輯，為簡化我們先直接分析
                summary = get_ai_summary(target['name'], text_content)
                send_telegram(f"【Pro 版監控: {target['name']}】\n\n{summary}\n\nSource: {target['url']}")
                
            except Exception as e:
                print(f"Failed {target['name']}: {e}")
        
        browser.close()

if __name__ == "__main__":
    run()
