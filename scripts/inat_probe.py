"""唯讀探針：確認 iNaturalist API 能否篩出「死亡」鳥類觀測（Alive or Dead 標註），並比較 NSW 近 28 天、前 28 天、去年同期。
每個查詢只要 per_page 1~5，不寫任何檔案。目的：評估「死亡鳥觀測」能否當已知疫區的間接監測指標。"""
import datetime, json
import requests

API = "https://api.inaturalist.org/v1"
UA = {"User-Agent": "au-h5n1-daily-report-probe/1.0 (read-only; contact via repo)"}
NSW = {"swlat": -37.6, "swlng": 140.9, "nelat": -28.1, "nelng": 153.7}


def get(path, **params):
    r = requests.get(f"{API}/{path}", params=params, headers=UA, timeout=40)
    return r.status_code, r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text[:200]


print("[iNat probe] --- controlled terms")
sc, d = get("controlled_terms")
term_id = value_id = None
if sc == 200:
    for t in d.get("results", []):
        if "alive" in t.get("label", "").lower():
            print(f"[iNat probe] term id={t['id']} label={t['label']!r} values={[(v['id'], v['label']) for v in t.get('values', [])]}")
            term_id = t["id"]
            for v in t.get("values", []):
                if v["label"].lower().startswith("dead"):
                    value_id = v["id"]
else:
    print(f"[iNat probe] controlled_terms HTTP {sc}: {d}")
print(f"[iNat probe] 採用 term_id={term_id} term_value_id(dead)={value_id}")

today = datetime.date.today()
def win(days_back_start, days_back_end):
    return ((today - datetime.timedelta(days=days_back_start)).isoformat(), (today - datetime.timedelta(days=days_back_end)).isoformat())

windows = {
    "近28天": win(28, 0),
    "前28天": win(56, 28),
    "去年同期(近28天)": win(28 + 365, 365),
}
for label, (d1, d2) in windows.items():
    base = dict(iconic_taxa="Aves", d1=d1, d2=d2, per_page=1, **NSW)
    sc1, all_ = get("observations", **base)
    row = {"all": all_.get("total_results") if sc1 == 200 else f"HTTP {sc1}"}
    if term_id and value_id:
        sc2, dead = get("observations", term_id=term_id, term_value_id=value_id, **base)
        row["dead"] = dead.get("total_results") if sc2 == 200 else f"HTTP {sc2}: {str(dead)[:80]}"
    print(f"[iNat probe] NSW 鳥類 {label} {d1}~{d2}: {row}")

if term_id and value_id:
    d1, d2 = windows["近28天"]
    sc, d = get("observations", iconic_taxa="Aves", d1=d1, d2=d2, term_id=term_id, term_value_id=value_id, per_page=8, order_by="observed_on", **NSW)
    for o in (d.get("results", []) if sc == 200 else []):
        tx = o.get("taxon") or {}
        print(f"[iNat probe 樣本] {o.get('observed_on')} {tx.get('preferred_common_name') or tx.get('name')} | {o.get('place_guess')} | grade={o.get('quality_grade')}")
