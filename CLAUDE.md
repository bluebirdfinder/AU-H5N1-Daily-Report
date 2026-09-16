# CLAUDE.md — 澳洲 H5N1 疫情監控與 Nestlé Purina Blayney 風險評估系統

本檔案給每次在此 repo 工作的 Claude 讀。專案背景、核心規則、已知資料完整性陷阱都寫在這裡，避免重蹈覆轍。

## 專案是什麼

雙產出的靜態網站系統，服務對象是評估 Nestlé Purina Blayney 廠（NSW）寵物食品原料供應鏈風險：

1. **疫情監控頁**（`index.html` / `index_en.html`）— 由 `h5n1.py` 執行 `compile_template()` 從 `report_template.html` / `report_template_en.html` **動態編譯**產生，每天兩次由 `.github/workflows/auto_update.yml` 自動跑。
2. **風險評估頁**（`risk_assessment.html` / `risk_assessment_en.html`）— **不是**模板編譯產物。`h5n1.py` 只有 `sync_risk_assessment_weekly()` 會碰它，且只改「歷次週報歸檔」彈窗的連結。其餘內容以前是人工手改的靜態 HTML，**2026-09-16 已改為讀取 `assets/js/cases_events.js`（`window.casesEventsEmbedded`）在載入時動態校正**（見下方「已修復」），但候鳥數字與部分敘述文字仍是靜態，改動前務必先看下面的清單。

**這個「一個全自動、一個半自動」的落差是本專案最大的資料完整性風險，修改前必讀。**

## 最高指導原則（來自 AGENT.md，勿違反）

- 台灣 BAPHIQ 檢疫是以「州（State）」為封鎖單位。NSW 境內**任一**商業家禽場確診 = 全州立即封鎖，與距離 Blayney 廠幾公里無關。
- 風險評估錨點必須是「NSW 商業家禽 0 確診」與「野鳥是否外溢至 NSW 商業聚落」，嚴禁用物理距離模糊焦點。
- 候鳥數據（eBird/Movebank/GBIF/ALA）是領先指標，不是終點指標；真正的紅線永遠是 NSW 商業場是否確診。

## 2026-09-16 稽核與修復摘要

### 已修復（程式碼層級）

1. **`h5n1.py` 新增 `write_cases_events_js()`**：每次編譯都把 `official_stats`（跟 `index.html` 的 `window.OFFICIAL_STATS` 同一份資料）寫到 `assets/js/cases_events.js`（`window.casesEventsEmbedded`）。`risk_assessment.html`/`_en.html` 原本就寫了讀這個全域變數的程式碼（`syncTimelineDataWithLiveStats()`），但從未有檔案真正賦值它，是死綁定——現在補上了。
2. **`parse_daff_official_stats()` 的離線 fallback 從寫死字典改為真的重新計算**：DAFF 官網連不上時，以前永遠退回函式最上方寫死的舊字典（長期停在 484 起/NSW 22 起）；`compute_stats_from_cases()`（用 `cases_events.json` 重新統計的權威回退方案）明明就存在，卻從來沒被呼叫過。現在 DAFF 連不上時會先呼叫它，用資料庫自己的最新內容回推，不會再退回好幾週前的數字。
3. **`risk_assessment.html`/`_en.html` 新增 `syncCaseEventsFromEmbedded()`**，在 `window.addEventListener('load', ...)` 第一步執行，把 NSW 卡片（`#kpi-nsw-events-val`）、科學矩陣的 NSW/VIC/SA 數字、`select-nsw-events` 下拉選單文字與分數分級、方法論 Modal 裡的「484 起」等全部改為讀 `window.casesEventsEmbedded` 動態產生，不再是寫死文字。
4. **`onload` 初始化鏈改成逐步 `try/catch`**：稽核時用 Playwright 實測發現，只要 Chart.js CDN 被擋（企業防火牆常見情境，這也是本專案自己在 README 反覆提到的痛點），`initRadarChart()` 一拋錯就會讓同一個監聽器裡後面所有步驟（包含決定風險分數的 `recalculateRisk()`）整串不執行，NSW 卡片、風險分數、Decision Zone badge 全部停在初始靜態值。現在每一步獨立 `try/catch`，一步失敗不影響其他步驟。
5. **`total_birds` 欄位名 bug**：`risk_assessment.html`/`report_template.html` 多處讀 `state_summary.NSW.total_birds`，這個欄位在 `bird_data.json` schema 裡不存在，永遠 fallback 到寫死值。已改為對 `high_risk_observations` 現場 `reduce` 加總（跟 `renderEbirdOnMap()` 原本就寫對的邏輯一致）。
6. **`report_template.html` 補上 `#ebird-total-obs`（首頁候鳥總數大字）的 JS 綁定**：以前完全沒有綁定，永遠顯示編譯當下的靜態文字。
7. **候鳥資料新鮮度警示**：`bird_data.json` 的 `fetched_at_utc` 超過 2 天沒更新時，兩個頁面都會顯示「⚠️ 資料已 N 天未更新」，不再讓使用者誤以為數字是即時的。
8. **雜項一致性修正**：Decision Zone Matrix 的「當前現況」註記改成動態貼到真正對應的分數區間卡片上（含 `isCommercialFarmInfected` 觸發時強制標在紅色區）；「商業禽場爆發 (+75分)」按鈕文字改成「強制封頂 100分」以符合 `recalculateRisk()` 的實際邏輯；Card 2（商業家禽與蛋場狀態）改成會跟著模擬器的商業禽場爆發開關變色，不再永遠顯示綠色安全；移除 `report_template.html`/`_en.html` 對 `gbif_bird_data.js`（193KB）的死重量載入（該頁從未讀取它）；ZH 版工廠地緣距離卡片補上 `MIN_DISTANCE_PLACEHOLDER`（EN 版本來就有，ZH 版之前漏掉，永遠顯示寫死的「215 公里」與具體卻可能過期的地名）。

驗證方式：以 Node Playwright（`file://` 直接開檔）逐一讀取上述 DOM 元素文字並比對 `cases_events.json`/`bird_data.json` 重新算出的 ground truth，確認一致；另外用 `setCommercialFarmStatus(1)` 模擬商業禽場破口情境，確認 Card 2、Decision Zone badge、風險分數三處連動正確。

### 尚未修復，需要人工決定或無法在此環境驗證

1. **`EBIRD_API_KEY` 這個 GitHub Secret 狀態未知**：`bird_data.json` 的 `fetched_at_utc` 截至稽核當下仍停在 `2026-09-04`。`fetch_ebird_data()` 在金鑰缺失/失效時只會印一行 log 靜默跳過，不會讓 workflow 失敗。只有能進 repo Settings → Secrets 的人能確認，Claude 看不到 secret 本身。
2. **`ala_bird_data.json` 從未產生過**：`fetch_ala_data()` 用裸 `requests.get()`，沒有像 `smart_fetch_url()` 對 DAFF 那樣的 curl_cffi/Playwright 降級鏈，疑似被 `biocache.ala.org.au` 擋掉。GBIF、Movebank 是正常每日更新的，不受影響。
3. **⚠️ `assets/js/purina_auth.js` 的「機密存取」密碼門完全是裝飾性的，不是真的資安控制**：這支檔案在前端硬編碼了明碼密碼清單，且驗證邏輯只是在頁面上蓋一層視覺遮罩（overlay），**底層 DOM 內容從頭到尾都完整存在，沒有被移除或加密**——稽核時用 Playwright 直接讀 DOM 就拿到全部風險評估數字，完全不需要通過這個「密碼驗證」。如果這個 repo 是公開的（README 提到部署在 `bluebirdfinder.github.io`），任何人打開瀏覽器開發者工具、`view-source`、或直接 `curl` 都能看到頁面宣稱的「商業機密與未公開流行病學遙測數據」，密碼門形同虛設。這不是這次稽核要修的範圍，但強烈建議與使用者確認：真的需要保密就不能只靠純前端密碼門，要嘛改成真正需要驗證的私有網站/伺服器，要嘛就不要在頁面文字宣稱「機密」造成錯誤的保密期待。

**教訓**：往後任何「這個數字對不對」的問題，先用 `python3` 對 `cases_events.json` / `bird_data.json` 重新算一次 ground truth，不要只看 HTML 顯示的字。畫面好看 ≠ 數字是活的；有 `id` 也不代表真的有 JS 在寫它，要親自 grep 確認賦值那一行存在。

## 開發規範

- CDN 白名單只能用 `cdnjs.cloudflare.com`，不可用 `cdn.jsdelivr.net` / `unpkg.com`（企業資安政策，見 AGENT.md）。
- 中英文四組檔案（`index`/`index_en`、`risk_assessment`/`risk_assessment_en`、`risk_assessment_slides`/`risk_assessment_slides_en`）必須維持同步；改一邊時記得另一邊——這次稽核發現的好幾個 bug 都是「中文版修過、英文版沒同步跟著改」（例如 NSW 事件數中文版寫 22、英文版某幾處寫的是完全不同的 17 或 456）。
- 改完 `h5n1.py` 或模板後，用 `python h5n1.py` 重新編譯，確認 console 印出「網頁自動編譯成功！」。在沒有 `EBIRD_API_KEY`/`MOVEBANK_USER`/網路權限的沙盒環境跑這支程式是安全的（每個抓取步驟都有 try/except 與離線 fallback），但跑完記得檢查 `git diff`，不要把沙盒才會出現的降級資料（例如網路不通導致 GBIF 寫出 0 筆記錄）誤 commit 回去。
- 需要稽核頁面數字或候鳥資料時，先用 `h5n1-data-audit` skill（`.claude/skills/h5n1-data-audit/SKILL.md`）。

## 檔案速查

| 檔案 | 角色 |
|---|---|
| `h5n1.py` | 抓取 + 編譯引擎，唯一會寫 JSON 資料檔、`index*.html` 與 `assets/js/cases_events.js` 的程式 |
| `report_template.html`/`_en.html` | `index.html`/`_en.html` 的原始模板（含 placeholder） |
| `risk_assessment.html`/`_en.html` | 風險模型頁，事件數字已動態化（讀 `cases_events.js`），候鳥數字/敘述文字仍多為靜態 |
| `cases_events.json` | 事件制病例資料庫（唯一 ground truth） |
| `assets/js/cases_events.js` | `cases_events.json`/`official_stats` 的免 CORS 打包版本（2026-09-16 新增），`risk_assessment.html` 靠這個檔案動態校正 |
| `bird_data.json` / `gbif_bird_data.json` / `movebank_tracks.json` | 三個候鳥數據源，新鮮度不一（eBird 常因 Secret 問題停更，GBIF/Movebank 正常） |
| `assets/js/*.js` | 上述 JSON 的免 CORS 打包版本，供 `file://` 離線開啟 |
