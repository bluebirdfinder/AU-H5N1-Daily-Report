"""唯讀探針：讀取維州農業局官網的圈養令相關頁面與公報 PDF，把頁面文字印進 log。不寫任何檔案、不改任何統計。
目的：查證「家禽圈養令是否已於 2026-10-16 解除」，以官方原文為準（Gemini 的說法尚未驗證）。"""
import subprocess, sys, tempfile, os
from playwright.sync_api import sync_playwright

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
BASE = "https://agriculture.vic.gov.au"
PAGES = {
    "A 新聞稿：圈養令結束": BASE + "/about/media-centre/media-releases/2026-releases/biosecurity-remains-essential-as-temporary-poultry-confinement-requirement-ends",
    "B 新聞稿：圈養令延長": BASE + "/about/media-centre/media-releases/2026-releases/requirement-to-prevent-poultry-contact-with-wild-birds-extended",
    "C H5 禽流感主頁": BASE + "/biosecurity/animal-diseases/poultry-diseases/H5N1-avian-influenza-H5-bird-flu",
    "D 舊專屬頁（11/18 起 404）": BASE + "/biosecurity/animal-diseases/poultry-diseases/H5N1-avian-influenza-H5-bird-flu/about-h5-bird-flu/control-order-housing-requirement",
}
GAZETTE = "https://www.gazette.vic.gov.au/gazette/Gazettes2026/GG2026S434.pdf"


def lines_of(text, limit):
    seen, out = set(), []
    for l in text.split("\n"):
        l = " ".join(l.split())
        if len(l) >= 15 and l not in seen:
            seen.add(l)
            out.append(l)
            if len(out) >= limit:
                break
    return out


with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_context(user_agent=UA, viewport={"width": 1300, "height": 2000}).new_page()
    for tag, url in PAGES.items():
        try:
            r = page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(2000)
            print(f"[VIC probe] === {tag} | HTTP {r.status if r else None} | final={page.url[:140]} | title={page.title()[:100]!r}")
            for l in lines_of(page.inner_text("body"), 70):
                print(f"[VIC probe 文字] {l[:400]}")
        except Exception as e:
            print(f"[VIC probe] === {tag} -> 例外 {type(e).__name__}: {str(e)[:150]}")
    # 公報 PDF：用瀏覽器 context 的請求下載（帶瀏覽器標頭），再用 pdftotext 轉文字
    try:
        resp = page.context.request.get(GAZETTE, timeout=60000)
        body = resp.body()
        print(f"[VIC probe] === 公報 PDF | HTTP {resp.status} | {len(body)} bytes | content-type={resp.headers.get('content-type')}")
        if resp.status == 200 and body[:4] == b"%PDF":
            f = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False); f.write(body); f.close()
            r = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, text=True)
            os.unlink(f.name)
            if r.returncode == 0:
                for l in lines_of(r.stdout, 90):
                    print(f"[VIC probe 公報] {l[:400]}")
            else:
                print(f"[VIC probe] pdftotext 失敗: {r.stderr[:150]}")
    except Exception as e:
        print(f"[VIC probe] 公報例外 {type(e).__name__}: {str(e)[:150]}")
    b.close()
