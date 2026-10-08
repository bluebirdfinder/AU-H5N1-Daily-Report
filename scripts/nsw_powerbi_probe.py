"""唯讀探針：載入 NSW bird-flu 頁面，找出 Power BI 嵌入並把攔截到的資料印進 log。不寫任何檔案。"""
import json
from playwright.sync_api import sync_playwright

URL = "https://www.nsw.gov.au/regional-and-primary-industries/biosecurity/bird-flu"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_context(user_agent=UA, viewport={"width": 1400, "height": 2200}).new_page()
    pbi = []

    def on_resp(r):
        u = r.url
        if "powerbi" in u or "analysis.windows.net" in u:
            try:
                body = r.text() if "querydata" in u or "modelsAndExploration" in u or "conceptualschema" in u else ""
            except Exception as e:
                body = f"<讀取失敗 {e}>"
            pbi.append((r.request.method, r.status, u, body))

    page.on("response", on_resp)
    resp = page.goto(URL, wait_until="networkidle", timeout=90000)
    print(f"[NSW probe] HTTP {resp.status if resp else None}, final url {page.url}, title {page.title()!r}")
    page.wait_for_timeout(8000)
    for i, fr in enumerate(page.frames):
        print(f"[NSW probe] frame {i}: {fr.url[:300]}")
    for el in page.query_selector_all("iframe"):
        print(f"[NSW probe] iframe src={el.get_attribute('src')!r} title={el.get_attribute('title')!r}")
    html = page.content()
    print(f"[NSW probe] 頁面 HTML {len(html)} 字元, 含 powerbi: {'powerbi' in html.lower()}")
    for line in page.inner_text("body").split("\n"):
        line = " ".join(line.split())
        if len(line) >= 20 and any(k in line.lower() for k in ("confirmed", "detect", "h5", "event", "total", "case", "last updated", "power bi")):
            print(f"[NSW probe 文字] {line[:300]}")
    for m, s, u, body in pbi:
        print(f"[NSW probe PBI] {m} {s} {u[:200]} ({len(body)} 字元)")
        if body:
            print(f"[NSW probe PBI body] {body[:6000]}")
    for fr in page.frames:
        if "powerbi" in fr.url:
            try:
                txt = fr.inner_text("body")
                flat = " | ".join(" ".join(l.split()) for l in txt.split("\n") if l.strip())
                print(f"[NSW probe PBI 畫面文字] {flat[:3000]}")
            except Exception as e:
                print(f"[NSW probe PBI 畫面文字] 失敗 {e}")
    b.close()
