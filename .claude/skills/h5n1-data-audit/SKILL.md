---
name: h5n1-data-audit
description: Audit and reconcile the AU H5N1 monitoring dashboard (index.html/index_en.html) and the risk assessment model (risk_assessment.html/_en.html + slides) against their real source-of-truth JSON files (cases_events.json, bird_data.json, gbif_bird_data.json, movebank_tracks.json). Use this whenever the user asks to check/verify/reconcile numbers on these pages, reports a stale or "stuck" metric (state event counts, bird counts, risk scores), asks whether the eBird/ALA/GBIF/Movebank API integration is broken, or wants a full architecture/data-flow inventory of these two pages before trusting them. Trigger on phrases like "對一下數字", "數字對不對", "核對", "API 是不是有 bug", "候鳥數量沒動", "risk assessment 準不準", or any request to self-audit this repo's HTML pages.
---

# H5N1 Dashboard Data Audit

這個 repo 有兩種頁面，資料新鮮度完全不同，稽核前必須先分清楚：

- **`index.html` / `index_en.html`**：`h5n1.py` 的 `compile_template()` 每次跑都會從 `report_template.html` 重新產生，數字理論上是活的。
- **`risk_assessment.html` / `risk_assessment_en.html` / `risk_assessment_slides*.html`**：`h5n1.py` 只有 `sync_risk_assessment_weekly()` 會碰，而且只改歷次週報歸檔彈窗的連結。裡面幾乎所有分數、州別事件數、候鳥數字都是**人工寫死的靜態文字**，不會因為 `cases_events.json` 或 `bird_data.json` 更新而自動改變。過去的稽核已證實這裡會長期凍結在某次手動編輯當下的數字（例如 2026-09-08 v2.9.0 的 NSW=22 一路凍結到 09-16，實際已經是 32）。

**核心原則：永遠不要相信 HTML 裡顯示的數字本身，一定要拿它去跟來源 JSON 重新算一次再比對。**

## Step 1 — 用 JSON 算出 ground truth

不要用肉眼掃 HTML 猜對不對。跑這段（邏輯完全比照 `h5n1.py` 的 `compute_stats_from_cases()`，同一套 `loc_map`）：

```bash
python3 -c "
import json
d = json.load(open('cases_events.json'))
loc_map = [
    ('WA',  ['西澳', 'WA']), ('SA',  ['南澳', 'SA']),
    ('VIC', ['維多利亞', 'VIC', '維州']), ('NSW', ['新南威爾斯', 'NSW', '新州']),
    ('QLD', ['昆士蘭', 'QLD', '昆州']), ('TAS', ['塔斯馬尼亞', 'TAS']),
    ('NT',  ['北領地', 'NT']), ('ACT', ['首都領地', 'ACT']),
]
evt = {st:0 for st,_ in loc_map}
for c in d:
    if c.get('type') != 'Confirmed': continue
    loc = c.get('location','')
    for st, kws in loc_map:
        if any(k in loc for k in kws):
            evt[st] += 1; break
print(evt, 'sum=', sum(evt.values()), '/ total records=', len(d))
"
```

比對這輸出跟 `risk_assessment.html` 裡出現的所有 `X 起` 文字（`grep -noE "(SA|VIC|WA|TAS|QLD|NSW)[^<]{0,20}[0-9]{1,4}\s*起" risk_assessment.html risk_assessment_en.html`），以及 `select-nsw-events` 下拉選單的 option 文字。凡是對不上的都是待修的落差，不是新 bug——是已知模式的又一次發生。

同樣邏輯套用在候鳥數字：

```bash
python3 -c "
import json
d = json.load(open('bird_data.json'))
obs = d.get('high_risk_observations', [])
print('fetched_at_utc:', d.get('fetched_at_utc'))
print('records:', len(obs), 'sum howMany:', sum((o.get('howMany') or 0) for o in obs))
nsw = [o for o in obs if o.get('state')=='NSW']
print('NSW records:', len(nsw), 'NSW sum howMany:', sum((o.get('howMany') or 0) for o in nsw))
"
```

`fetched_at_utc` 若停在多天前（超過 workflow 排程週期，目前是每天 2 次），就是 API 沒在更新，不是前端顯示問題——先查第 2 步。

## Step 2 — 候鳥數字「沒動」時的排查順序

1. **`bird_data.json` 的 `fetched_at_utc` 有沒有更新？** 沒有 → `fetch_ebird_data()`（h5n1.py 約 2356 行）大概率因為 `EBIRD_API_KEY` 這個 GitHub Secret 沒設或失效而**靜默 return**（`if not ebird_key: return`，只印 log，不會讓 workflow 失敗，也不會有任何前端可見的錯誤提示）。這個要請使用者去 repo Settings → Secrets 確認，Claude 自己看不到 secret 是否存在。
2. **就算 JSON 有更新，前端數字還是沒動？** 檢查是不是綁定邏輯本身壞掉：
   - 找 `state_summary.NSW.total_birds` 這種欄位名 —— `bird_data.json` 的 schema 只有 `total_obs` / `risk_species_obs` / `region_code`，沒有 `total_birds`，凡是讀這個欄位的地方永遠拿到 `undefined`，會 fallback 到寫死的預設值（286 / 651 / 1407 都出現過，取決於哪次手改）。正確作法是像 `risk_assessment.html` 的 `renderEbirdOnMap()` 那樣，對 `high_risk_observations` 陣列做 `reduce((sum,o)=>sum+(o.howMany||1),0)` 現場加總，不要指望 JSON 裡有現成的加總欄位。
   - 確認顯示數字的 DOM 元素真的有對應的 `document.getElementById(...).textContent = ...` 賦值。曾發現 `report_template.html` 的 `#ebird-total-obs`（首頁候鳥總數大字）完全沒有任何 JS 更新它，是純靜態文字。
3. **ALA / GBIF / Movebank 各自獨立檢查**，不要假設三個源共病：GBIF、Movebank 目前運作正常（有每日 git commit 佐證，`git log --oneline -- gbif_bird_data.json` 可查）；ALA (`ala_bird_data.json`) 過去稽核發現這個檔案從未被產生過，`fetch_ala_data()` 用裸 `requests.get()`，沒有像 `smart_fetch_url()` 那樣的 curl_cffi/Playwright 降級鏈，疑似被目標網站擋掉又把例外吃掉。

## Step 3 — 建立架構/資料流盤點表

被要求「列出功能區塊表」時，欄位固定用：**前端功能區塊 | 功能 | 資料來源 | 程式碼位置 | 是否稽核 | 稽核發現**。針對兩個頁面分別列，並標明每個區塊的資料來源屬於三類之一：

- **動態（Python 模板變數）**：由 `h5n1.py` 的某個 `generate_dynamic_*()` 函式產生後替換 `<!-- ..._PLACEHOLDER -->`。
- **動態（JS 讀取 embedded JSON）**：頁面載入時讀 `window.*Embedded`（來自 `assets/js/*.js`），有 `document.getElementById(...).textContent=...` 這種賦值語句。
- **靜態（寫死文字）**：HTML 裡直接出現的數字/文字，找不到對應的變數替換或 DOM 賦值。這類是風險評估頁的大宗，也是資料落差的來源。

檔案很大（`index.html` 473KB、`risk_assessment.html` 178KB），不要整檔讀入；先 `grep -n` 關鍵字（區塊標題、`id="..."`、`function ...(`）鎖定行號區間，再用 `Read` 搭配 `offset`/`limit` 精讀該區塊。

## Step 4 — 回報格式

- 先講 ground truth 數字 vs 頁面顯示數字的落差表（州別、候鳥），再講根因（哪個函式/哪一行/哪個欄位名錯）。
- 修 bug 前，先確認是要順便修掉，還是使用者只要稽核報告——`risk_assessment.html` 的數字要嘛靠自動化重新產生機制（目前不存在，屬於架構缺口，不是單純打錯字），要嘛人工同步；這是要跟使用者確認的產品決策，不要自己擅自決定要不要新增一個自動編譯 risk_assessment 的 pipeline。
- 修完任何跟中文版同步的檔案，記得比對英文版（`_en.html`）是否有相同的寫死數字要一起改，過去發現兩邊是複製貼上的，同一個 bug 兩份都有。
