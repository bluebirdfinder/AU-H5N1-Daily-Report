# 專案開發與 Bug 修正軌跡日誌 (Walkthrough Log)

## 2026-08-12 雙層獨立版塊 (Dual-Section Architecture) 網頁大升級

### 📌 重構目標與版面架構
應使用者需求，報告網頁已全面重構為**「上下雙層完全獨立專區」**架構：

1. **【上半部】最新事件導向即時監測專區 (`#live-events-section`)**：
   - 專注於 DAFF 2026-08-12 起最新國際標準：**全澳 151 起確診事件 (Positive Events)**、**1,307 起陰性排除** 與 **18,118 筆熱線通報**。
   - **完全不出現單鳥「0 隻」或隻數字樣**。
   - 包含獨立之**最新中文摘要、事件動態儀表板 (Event KPIs)、事件每週增長趨勢圖 (`eventTrendChart` - 雙 Y 軸)、151 起事件點位地圖 (`eventMap` - 帶序號發光圓圈)、151 起可滾動與可搜尋排序明細表 (`eventTableBody`)**。

2. **【中間區塊】DAFF 2026-08-12 數據規範切換告示欄 (`#policy-transition-divider`)**：
   - 標註生效時間：**2026 年 8 月 12 日 19:00 AEST (台北時間 17:00)**。
   - 包含完整流行病學改版原因說明（野生動物廣泛傳播期與 WOAH/FAO 事件導向資源優化），並宣告下半部歷史隻數庫完整封存告示。

3. **【下半部】歷史隻數 (236 隻) 完整凍結資料庫專區 (`#historical-birds-section`)**：
   - 完整紀錄截至 2026-08-12 17:00 AEST 官方凍結計數前之 **236 隻單鳥確診 / 55 起歷史個案**（南澳 163 隻、維州 58 隻、西澳 10 隻、新州 4 隻、昆州 1 隻）。
   - 包含獨立之**歷史中文摘要、歷史隻數儀表板 (Bird KPIs)、歷史隻數每週增長趨勢圖 (`historicalBirdChart` - 完全還原圖 A 雙 Y 軸)、歷史隻數點位與發光紅藍綠圓圈地圖 (`historicalBirdMap` - 完全還原圖 B 帶鳥隻數字 Badge)、歷史 64 筆詳細病歷記錄表 (`historicalBirdTableBody`)**。

4. **【全新升級】表格欄位點擊排序 (Click-to-Sort) 與即時關鍵字搜尋 (Search Filter)**：
   - **點擊排序**：上下表格所有欄位標頭均支援點擊切換升冪 `▲` / 降冪 `▼`。
   - **即時過濾**：提供對話輸入框，支援鍵入 `NSW`、`VIC`、`Casey`、`Esperance`、`確診` 或特定日期，即時過濾顯示符合條件的案例。

---

### 🧪 Playwright 自動化實測結果
透過無頭瀏覽器驗證 `index.html`：
- **Section 1 151 起事件表格**：151 筆完整加載，`nsw` 關鍵字即時過濾出 4 筆新州個案，欄位點擊排序順暢切換。
- **Section 2 歷史 64 筆個案表格**：64 筆完整加載，排序與過濾功能完全正常。
- **雙地圖與雙趨勢圖**：全數 100% 渲染成功！

---

## 2026-08-13 排程優化、雙引擎 AI 升級與關鍵 Bug 修復

### 📌 背景：DAFF 17:00 AEST 結算規範確認
根據 DAFF 官網最新 Disclaimer 免責聲明條款：
> *"Data reflects information provided by state and territory governments to the Australian Government as at 17:00 AEST daily."*

官方每日固定於 **17:00 AEST** 完成全澳各州與領地之 H5N1 數據匯總與結算。舊排程的第一班（AEST 15:00 / 台灣 13:00）比官方結算點早了 2 小時，導致下午無法即時捕捉當天發布。

### ⚙️ 自動排程優化
工作流 `.github/workflows/auto_update.yml` 已重構為雙班次對齊架構：
1. **主抓班次 (台灣時間 16:00 / AEST 18:00 / UTC 08:00)**：於 DAFF 17:00 AEST 結算後 1 小時精準抓取。
2. **早晨覆核班次 (台灣時間 07:00 / AEST 09:00 / UTC 23:00)**：備援掃瞄，同時捕捉各州官網與澳洲媒體 RSS 即時動態。

### 🚀 雙引擎 (Dual-Engine) AI 架構升級
1. **新聞摘要：Gemini API Google Search Grounding 實時連網**
   整合 Gemini API 的 `tools: [{"google_search": {}}]` 功能，每次執行時 Gemini 主動搜尋當下最新澳洲 H5N1 報導，產出零時差即時中文報導摘要（自動捕捉如 TAS 首起棕賊鷗案例等突發新聞）。
2. **指標/地圖：確定性數據庫 + 對帳防護罩**
   KPI 卡片、GIS 地圖與事件明細表維持由 `cases_events.json` 運算，確保數據 100% 精確且無 AI 幻覺。
3. **TAS 塔斯馬尼亞整合**：
   已加入 TAS 官方頁面並新增 `Brown Skua / 棕賊鷗` 關鍵字標籤。

### 🐛 重大 Bug 修復（四項）

#### Bug #1【最致命】`main()` 永遠跳過 DAFF 爬取
- **問題**：舊邏輯 `if len(events_cases) < 151: fetch_daff_updates()` — `cases_events.json` 已有 151 筆後，條件永遠為 `False`，`fetch_daff_updates()` 從未執行，DAFF 數字永遠凍結在 151。
- **修復**：移除條件判斷，永遠執行 `fetch_daff_updates()`。DAFF 數字當日已從 151 暴增至 **186 起（SA 123 / VIC 48）**，修復後網頁立即反映最新數字。

#### Bug #2 `gemini-2.0-flash` 已被 Google 廢棄（404）
- **問題**：GitHub Actions 日誌顯示 `"This model models/gemini-2.0-flash is no longer available"`，浪費一次 API 呼叫延遲才降級。
- **修復**：兩處 model list（Vision API + Grounding API）移除廢棄模型，改以 `gemini-2.5-flash → gemini-2.5-flash-lite → gemini-1.5-flash-latest` 為優先順序。

#### Bug #3 `parse_daff_official_stats()` Fallback 預設值過時
- **問題**：Fallback 仍是舊的 151/SA93/VIC43，若 DAFF 官網斷線，網頁顯示舊數字。
- **修復**：Fallback 同步更新至 DAFF 2026-08-13 最新值（186/SA123/VIC48/1273陰性/18869通報）；同時補加 TAS（塔斯馬尼亞）的州別解析模式。

#### Bug #4 `auto_fill_state_shortfalls()` 單位混用（事件數 vs. 鳥隻數）
- **問題**：此函數設計用於歷史鳥隻數對帳（比對 236 隻），卻被誤用於事件資料庫（cases_events.json），把 152 起事件誤判為「少了 84 隻鳥」，每次執行都虛增幻象紀錄。
- **修復**：在 `fetch_daff_updates()` 中停用此函數對事件庫的呼叫（加詳細停用說明註解）。

### 🆕 方案 A：數據來源透明標示

**設計目標**：讓使用者一眼辨識網頁數字是「即時 DAFF 爬取」還是「備援硬編碼值」。

**實作方式**：
- `parse_daff_official_stats()` 成功解析時寫入 `"source": "live"` 與 `"scrape_time": "2026-08-13 08:14 UTC"`；連線失敗時寫入 `"source": "fallback"`。
- `report_template.html` 頂部橫幅由 JS 讀取 `window.OFFICIAL_STATS.source`，動態套用顏色與文字：

| 狀態 | 橫幅顏色 | 內容 |
|:---:|:---:|:---|
| `source: "live"` | 🟢 綠色 + 閃爍點 | `✅ 即時官方數據 · 已與 DAFF 官網同步 (2026-08-13 08:14 UTC) — 全澳 186 起確診...` |
| `source: "fallback"` | 🟡 橘色 + 靜止點 | `⚠️ 備援數據 · DAFF 官網連線異常，目前顯示硬編碼預設值（非即時）...` |
