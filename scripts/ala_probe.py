"""唯讀探針：從 GitHub runner 對 ALA 的幾個入口各發一次最小請求（pageSize=1），印出狀態碼、關鍵回應標頭與前 300 字。
不寫任何檔案、不改任何統計。目的：判斷 ALA 的阻擋是 IP 層級、還是特定入口(網站後端 vs 官方 API 閘道)才擋。"""
import os, sys, urllib.parse
import requests

try:
    from curl_cffi import requests as cffi
except Exception:
    cffi = None

QS = {"q": "country:Australia", "fq": "family:Laridae", "pageSize": 1, "sort": "eventDate", "dir": "desc"}
TARGETS = {
    "A 現用 biocache.ala.org.au/ws": "https://biocache.ala.org.au/ws/occurrences/search",
    "B 官方 API 閘道 api.ala.org.au": "https://api.ala.org.au/occurrences/occurrences/search",
    "C 直連 biocache-ws.ala.org.au": "https://biocache-ws.ala.org.au/ws/occurrences/search",
}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
KEEP = ("server", "cf-ray", "x-cache", "via", "content-type", "retry-after", "x-amzn-requestid", "x-request-id")


def show(tag, status, headers, text):
    hdr = {k: v for k, v in headers.items() if k.lower() in KEEP}
    flat = " ".join((text or "").split())[:300]
    print(f"[ALA probe] {tag} -> HTTP {status}, {len(text or '')} 字元, headers={hdr}")
    print(f"[ALA probe]   body: {flat}")


def run(tag, fn):
    try:
        show(tag, *fn())
    except Exception as e:
        print(f"[ALA probe] {tag} -> 例外 {type(e).__name__}: {str(e)[:150]}")


print(f"[ALA probe] curl_cffi 可用: {cffi is not None}")
for name, base in TARGETS.items():
    url = base + "?" + urllib.parse.urlencode(QS)

    def plain(url=url):
        r = requests.get(url, headers={"User-Agent": UA, "Accept": "application/json"}, timeout=25)
        return r.status_code, r.headers, r.text

    run(f"{name} | requests", plain)
    if cffi:
        def imp(url=url):
            r = cffi.get(url, impersonate="chrome124", timeout=25)
            return r.status_code, r.headers, r.text

        run(f"{name} | curl_cffi chrome124", imp)

# CF Worker 路徑：與 h5n1.py smart_fetch_url() 第 2 段相同呼叫方式，但印出完整狀態與內容（Secret 值不會被印出）
worker = os.environ.get("CF_WORKER_URL", "").strip().rstrip("/")
if worker:
    for name, base in list(TARGETS.items())[:2]:
        target = base + "?" + urllib.parse.urlencode(QS)

        def via_worker(target=target):
            r = requests.get(f"{worker}?url={urllib.parse.quote(target)}", timeout=30)
            return r.status_code, r.headers, r.text

        run(f"{name} | CF Worker", via_worker)
else:
    print("[ALA probe] 未設定 CF_WORKER_URL，略過 Worker 測試")

# 驗證正式抓取函式（改用 api.ala.org.au 後）：直接跑 h5n1.fetch_ala_data()，只在 runner 暫存目錄寫檔，不 commit
if os.environ.get("RUN_FETCH") == "1":
    sys.path.insert(0, os.getcwd())
    import json
    import h5n1
    h5n1.fetch_ala_data()
    try:
        d = json.load(open("ala_bird_data.json", encoding="utf-8"))
        print(f"[ALA probe 正式函式] available={d.get('available')} reason={d.get('unavailable_reason')!r} "
              f"records={d.get('sample_records_count')} total_in_ala={d.get('total_matched_in_ala')} states={d.get('state_counts')}")
        for o in d.get("observations", [])[:5]:
            print(f"[ALA probe 正式函式] sample: {o}")
    except Exception as e:
        print(f"[ALA probe 正式函式] 讀取輸出失敗: {e}")
