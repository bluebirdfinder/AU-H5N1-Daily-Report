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
   - **點擊排序**：上下表格所有欄位標頭（案件編號、通報日期、發現日期、確診隻數、地理位置、物種、判定狀態）均支援點擊切換升冪 `▲` / 降冪 `▼`。
   - **即時過濾**：提供對話輸入框，支援鍵入 `NSW`、`VIC`、`Casey`、`Esperance`、`確診` 或特定日期，即時過濾顯示符合條件的案例。

---

### 🧪 Playwright 自動化實實測試結果
透過無頭瀏覽器驗證 `index.html`：
- **Section 1 151 起事件表格**：151 筆完整加載，`nsw` 關鍵字即時過濾出 4 筆新州個案，欄位點擊排序順暢切換。
- **Section 2 歷史 64 筆個案表格**：64 筆完整加載，排序與過濾功能完全正常。
- **雙地圖與雙趨勢圖**：全數 100% 渲染成功！

---

## 2026-08-13 澳洲 DAFF 17:00 AEST 結算規範對齊與 GitHub Actions 自動排程優化

### 📌 關鍵發現與背景
根據 DAFF 官網最新 Disclaimer 免責聲明條款：
> *"Data reflects information provided by state and territory governments to the Australian Government as at 17:00 AEST daily."*

官方每日固定於 **17:00 AEST** 完成全澳各州與領地之 H5N1 數據匯總與結算。舊排程的第一班（AEST 15:00 / 台灣 13:00）比官方結算點早了 2 小時，導致下午無法即時捕捉當天發布。

### ⚙️ 自動排程優化與雙保險機制
工作流 [.github/workflows/auto_update.yml](file:///c:/Users/TWLaiAl/OneDrive%20-%20NESTLE/Nestle/Antigravity/AU_H5N1_Daily_Update/.github/workflows/auto_update.yml) 已重構為雙班次完美對齊架構：
1. **主抓班次 (台灣時間 16:00 / AEST 18:00 / UTC 08:00)**：給予 DAFF 17:00 AEST 結算後 1 小時作業緩衝，精準抓取最新國家級數據。
2. **早晨覆核班次 (台灣時間 07:00 / AEST 09:00 / UTC 23:00)**：持續備援掃瞄，同時捕捉各州政府官網（如 NSW DPIRD, VIC Agriculture Victoria, SA PIRSA, TAS Biosecurity）與澳洲媒體 RSS（如 ABC News）在非官方結算時間發布的動態新聞與事件。

### 🚀 雙引擎 (Dual-Engine) AI 架構大升級
1. **新聞摘要：Gemini API Google Search Grounding 實時連網**  
   在 `generate_gemini_grounded_summary()` 函數中整合 Gemini API 的 `tools: [{"google_search": {}}]` 功能。每次執行時，Gemini 會像真人一樣主動去 Google 搜尋當下最新澳洲 H5N1 報導與各州官方公告（自動捕捉如塔斯馬尼亞州 TAS 首起棕賊鷗案例、維州新增案例等突發新聞），產出無時差的即時中文報導摘要。
2. **指標/地圖：確定性數據庫 + 對帳防護罩**  
   儀表板 KPI 卡片、GIS 地圖與事件明細表維持由 `cases_events.json` 數據庫運算，結合強大的對帳引擎，確保數據 100% 精確且無 AI 幻覺。
3. **TAS 塔斯馬尼亞專區整合**：  
   已加入 TAS 官方頁面 (`https://nre.tas.gov.au/biosecurity-tasmania/animal-biosecurity/animal-health/poultry-and-pigeons/bird-flu`) 並新增 `Brown Skua / 棕賊鷗` 關鍵字標籤。


