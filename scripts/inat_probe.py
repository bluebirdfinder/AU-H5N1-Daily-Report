"""唯讀探針（第二輪）：NSW 海岸海鳥／猛禽類群的 iNaturalist「死亡」標註，以 28 天為窗，比較近 5 窗與去年同期。
只用 per_page=0 取 total_results；不寫任何檔案。第一輪（全鳥類）：死亡占比近28天 0.61%／前28天 0.50%／去年同期 0.57%，
樣本多為常見陸鳥（撞玻璃、路殺），所以要拆到與 H5N1 相關的類群。"""
import datetime, time
import requests

API = "https://api.inaturalist.org/v1"
UA = {"User-Agent": "au-h5n1-daily-report-probe/1.0 (read-only; contact via repo)"}
NSW = {"swlat": -37.6, "swlng": 140.9, "nelat": -28.1, "nelng": 153.7}
TERM, DEAD = 17, 19
GROUPS = {
    "海岸海鳥": ["Laridae", "Stercorariidae", "Procellariidae", "Spheniscidae", "Phalacrocoracidae", "Sulidae", "Pelecanidae"],
    "猛禽": ["Accipitridae", "Falconidae"],
}


def get(path, **params):
    time.sleep(1.1)  # iNaturalist 建議 <= 60 requests/min
    r = requests.get(f"{API}/{path}", params=params, headers=UA, timeout=40)
    r.raise_for_status()
    return r.json()


ids = {}
for fams in GROUPS.values():
    for f in fams:
        res = get("taxa", q=f, rank="family", per_page=5).get("results", [])
        hit = next((t for t in res if t.get("name") == f), None)
        ids[f] = hit["id"] if hit else None
print(f"[iNat probe] 科別 taxon id: {ids}")

today = datetime.date.today()
for gname, fams in GROUPS.items():
    tids = ",".join(str(ids[f]) for f in fams if ids.get(f))
    if not tids:
        print(f"[iNat probe] {gname}: 無法解析 taxon id，略過")
        continue
    print(f"[iNat probe] === {gname}（taxon_id={tids}）每 28 天一窗：起~迄 | 今年 all/dead | 去年同期 all/dead")
    for i in range(5):
        end = today - datetime.timedelta(days=28 * i)
        start = end - datetime.timedelta(days=28)
        row = []
        for shift in (0, 364):
            d1 = (start - datetime.timedelta(days=shift)).isoformat()
            d2 = (end - datetime.timedelta(days=shift)).isoformat()
            base = dict(taxon_id=tids, d1=d1, d2=d2, per_page=0, **NSW)
            a = get("observations", **base)["total_results"]
            d = get("observations", term_id=TERM, term_value_id=DEAD, **base)["total_results"]
            row.append((a, d))
        (a0, d0), (a1, d1_) = row
        print(f"[iNat probe] {gname} {start}~{end} | 今年 {a0}/{d0} ({(100*d0/a0 if a0 else 0):.2f}%) | 去年 {a1}/{d1_} ({(100*d1_/a1 if a1 else 0):.2f}%)")

# 近 28 天海岸海鳥死亡樣本
tids = ",".join(str(ids[f]) for f in GROUPS["海岸海鳥"] if ids.get(f))
d2 = today.isoformat(); d1 = (today - datetime.timedelta(days=28)).isoformat()
res = get("observations", taxon_id=tids, d1=d1, d2=d2, term_id=TERM, term_value_id=DEAD, per_page=15, order_by="observed_on", **NSW).get("results", [])
for o in res:
    tx = o.get("taxon") or {}
    print(f"[iNat probe 樣本] {o.get('observed_on')} {tx.get('preferred_common_name') or tx.get('name')} | {o.get('place_guess')} | grade={o.get('quality_grade')}")
