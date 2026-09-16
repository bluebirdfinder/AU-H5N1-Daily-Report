# CLAUDE.md — 澳洲 H5N1 疫情監控與 Nestlé Purina Blayney 風險評估系統

本檔案給每次在此 repo 工作的 Claude 讀。專案背景、核心規則、已知資料完整性陷阱都寫在這裡，避免重蹈覆轍。

## 專案是什麼

雙產出的靜態網站系統，服務對象是評估 Nestlé Purina Blayney 廠（NSW）寵物食品原料供應鏈風險：

1. **疫情監控頁**（`index.html` / `index_en.html`）— 由 `h5n1.py` 執行 `compile_template()` 從 `report_template.html` / `report_template_en.html` **動態編譯**產生，每天兩次由 `.github/workflows/auto_update.yml` 自動跑。
2. **風險評估頁**（`risk_assessment.html` / `risk_assessment_en.html`）— **不是**模板編譯產物。`h5n1.py` 只有 `sync_risk_assessment_weekly()` 會碰它，而且只改「歷次週報歸檔」彈窗的連結，其餘 95% 的內容（風險分數、事件數字、候鳥數字、下拉選單文字）是**人工手改的靜態 HTML/JS**，不會隨 `cases_events.json` 或 `bird_data.json` 更新自動同步。

**這個「一個動態、一個半靜態」的落差是本專案最大的資料完整性風險，修改前必讀。**

## 最高指導原則（來自 AGENT.md，勿違反）

- 台灣 BAPHIQ 檢疫是以「州（State）」為封鎖單位。NSW 境內**任一**商業家禽場確診 = 全州立即封鎖，與距離 Blayney 廠幾公里無關。
- 風險評估錨點必須是「NSW 商業家禽 0 確診」與「野鳥是否外溢至 NSW 商業聚落」，嚴禁用物理距離模糊焦點。
- 候鳥數據（eBird/Movebank/GBIF/ALA）是領先指標，不是終點指標；真正的紅線永遠是 NSW 商業場是否確診。

## 已知資料落差 / Bug（2026-09-16 稽核發現，修復前請先確認是否仍存在）

1. **`risk_assessment.html`/`_en.html` 的州別事件數是凍結快照**：目前寫死 NSW=22、SA=271、VIC=150（v2.9.0 時期，2026-09-08），但 `cases_events.json` 實際已達 NSW=32、SA=295、VIC=165、TAS=37（用 `compute_stats_from_cases()` 的 `loc_map` 邏輯重新統計可驗證）。`index.html` 走的是動態管線，數字是對的；`risk_assessment.html` 沒有對應的重新產生機制。
2. **`bird_data.json`（eBird 實測）只在初始上傳時寫入過一次**：`git log -- bird_data.json` 只有一筆 `Add files via upload`，`fetched_at_utc` 停在 `2026-09-04`。`fetch_ebird_data()`（h5n1.py:2356）在 `EBIRD_API_KEY` 未設定或無效時會**靜默 return**，不會報錯、不會讓 workflow 失敗，只在 log 印一行沒人看的訊息。修這個要先確認 GitHub repo secret `EBIRD_API_KEY` 是否存在/有效。
3. **就算 eBird API 修好，前端多處綁定也是壞的**：
   - `risk_assessment.html` 2271 行、`report_template.html` 408 行都寫 `state_summary.NSW.total_birds`，但 `bird_data.json` 的 schema 根本沒有 `total_birds` 這個欄位（只有 `total_obs` / `risk_species_obs` / `region_code`），所以永遠落到寫死的 fallback（286 / 651 / 1407，視版本而定）。
   - `report_template.html` 的 `#ebird-total-obs`（首頁「🦅 野外目擊數量」大數字）**完全沒有 JS 綁定**，`updateHud()` 只更新 NSW 那行文字和時間戳，AU 總數字是純靜態文字，永遠不會變。
4. **`ala_bird_data.json` 從未產生過**：`fetch_ala_data()` 用裸 `requests.get()`（沒有 curl_cffi / Playwright 降級鏈，跟 `smart_fetch_url()` 對 DAFF 的處理不同），疑似被 ALA 網站擋掉，異常被吃掉沒有留痕跡。
5. GBIF (`gbif_bird_data.json`) 與 Movebank (`movebank_tracks.json`) 是正常每日更新的，不在上述問題範圍內，可信。
6. **`risk_assessment.html` 從未真正讀過 `cases_events.json`**：頁面裡唯一嘗試接活資料的函式 `syncTimelineDataWithLiveStats()`（約 1890 行）判斷 `window.casesEventsEmbedded`，但整個 repo 沒有任何一支 script 會賦值這個全域變數（`grep -r casesEventsEmbedded` 確認），是死程式碼。NSW 卡片（`#kpi-nsw-events-val`，約 228 行）雖然有 `id`，但同樣沒有任何 JS 寫入它——純文字寫死 `22`，這就是使用者回報「NSW 事件數不對」的直接根源，同一頁內 VIC/SA 的數字（科學矩陣區塊）也是同一批 2026-09-08 的舊快照。
7. **同一份 `risk_assessment.html` 內部就自相矛盾**，不用比對外部資料也看得出來：2 年時間軸圖表用 `498`，方法論 Modal 用 `484`（同一個「全澳確診事件」指標）；風險量表顯示分數 `37`，決策矩陣卡片卻寫「當前現況: 28」；商業禽場開關按鈕標「+75分」，但 `recalculateRisk()` 實際是直接把 NSW 分數強制設成 `100`（不是加 75）。修任何一個數字前，先確認同頁其他地方有沒有同一指標的另一份舊快照。
8. `ala_bird_data.json` 用裸 `requests.get()` 抓 `biocache.ala.org.au`，沒有像 `smart_fetch_url()` 對 DAFF 那樣的 curl_cffi/Playwright 降級鏈，疑似長期被擋、例外被吞掉，檔案從未成功產生過。`index.html` 的 `<head>` 也載入了 `gbif_bird_data.js`（193KB）但頁面自己的 JS 完全沒有讀取它，是白白載入的死重量。

**教訓**：往後任何「這個數字對不對」的問題，先用 `python3` 對 `cases_events.json` / `bird_data.json` 重新算一次 ground truth，不要只看 HTML 顯示的字。畫面好看 ≠ 數字是活的。

## 開發規範

- CDN 白名單只能用 `cdnjs.cloudflare.com`，不可用 `cdn.jsdelivr.net` / `unpkg.com`（企業資安政策，見 AGENT.md）。
- 中英文四組檔案（`index`/`index_en`、`risk_assessment`/`risk_assessment_en`、`risk_assessment_slides`/`risk_assessment_slides_en`）必須維持同步；改一邊時記得另一邊。
- 改完 `h5n1.py` 或模板後，用 `python h5n1.py` 重新編譯，確認 console 印出「網頁自動編譯成功！」。
- 完整 7 步驟發布 SOP 見 `SOP.md`；抓取架構與抗封鎖策略見 `GOVT_SCRAPING_BEST_PRACTICES.md`。
- 需要稽核頁面數字或候鳥資料時，先用 `/h5n1-data-audit` skill（`.claude/skills/h5n1-data-audit/SKILL.md`）。

## 檔案速查

| 檔案 | 角色 |
|---|---|
| `h5n1.py` | 抓取 + 編譯引擎，唯一會寫 JSON 資料檔與 `index*.html` 的程式 |
| `report_template.html`/`_en.html` | `index.html`/`_en.html` 的原始模板（含 placeholder） |
| `risk_assessment.html`/`_en.html` | 半靜態風險模型頁，**大部分數字要人工維護** |
| `cases_events.json` | 事件制病例資料庫（唯一 ground truth，見上方落差 #1） |
| `bird_data.json` / `gbif_bird_data.json` / `movebank_tracks.json` | 三個候鳥數據源，新鮮度不一（見落差 #2） |
| `assets/js/*.js` | 上述 JSON 的免 CORS 打包版本，供 `file://` 離線開啟 |
