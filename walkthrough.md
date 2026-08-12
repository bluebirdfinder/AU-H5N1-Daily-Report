# 專案開發與 Bug 修正軌跡日誌 (Walkthrough Log)

## 2026-08-12 DAFF 官方數據通報規範大改版升級 (Event-Based Reporting Transition)

### 📌 變更背景與官方聲明
澳洲聯邦農業部 (DAFF) 於 **2026 年 8 月 12 日晚間 19:00 (AEST)** 正式宣告通報規範升級：
> *“From 12 August 2026, we have changed how we report on H5 bird flu detections. Reporting will be based on events, rather than individual bird detections, where an event may involve one or more birds... As H5 bird flu is confirmed in more locations and species in Australia it will not be necessary to continue testing all species in known areas of transmission.”*

因應野生鳥類社區傳播擴大，官方正式由「單隻鳥隻數量統計 (236 隻)」轉為國際標準的**「確診事件導向 (Positive Events)」**，不再持續統計或公佈單鳥計數。

---

### 🛠️ 雙軌資料庫與前端 UI 重構說明

1. **資料庫新舊雙軌保留 (Dual-Track Database Architecture)**：
   - **`cases.json`（歷史單鳥隻數備份 - 完全凍結不覆寫）**：完整封封保存截至 2026-08-12 17:00 AEST 官方凍結之全澳 236 隻單鳥確診 / 55 起事件歷史資料庫。
   - **`cases_events.json`（動態事件資料庫 - 8/12 起即時追蹤）**：獨立開設新檔，專門存放 2026-08-12 19:00 AEST 官方改版後之 151 起 Positive Events 動態事件節點。

2. **前端 UI 與數字對齊**：
   - **頂部 Banner**：`✅ 已與澳洲聯邦農業部 (DAFF) 官網最新政策同步 (全澳累計 151 起確診事件 / 1,307 起陰性排除)`
   - **KPI 數據卡片**：`151 起確診事件`（下附 `1,307 起陰性排除事件 / 18,118 筆熱線通報`）
   - **各州確診事件細分 (Events by State)**：
     - 南澳 (SA): **93 起事件**
     - 維州 (VIC): **43 起事件**
     - 西澳 (WA): **10 起事件**
     - 新州 (NSW): **4 起事件**
     - 昆州 (QLD): **1 起事件**
     - *(總和 93 + 43 + 10 + 4 + 1 = 151 起事件)*
   - **政策改版告示橫幅**：在報告頂部加入藍色宣告欄，清楚說明 DAFF 8/12 數據規範改版原因與新舊雙軌保存機制。

3. **地方政府專區 URL 更新**：
   - **維多利亞州 (Agriculture Victoria)** 專區網址失效修正：已更新為最新 URL `https://agriculture.vic.gov.au/biosecurity/animal-diseases/poultry-diseases/H5N1-avian-influenza-H5-bird-flu` (Status 200 OK)。

---

### 🧪 實時驗證結果

透過 Playwright 無頭瀏覽器實際載入編譯後的 `index.html` 進行全流程自動化測試：
- **控制台 Console 錯誤**：`0`（完全無 JS 語法或載入錯誤）。
- **畫面渲染**：頂部告示橫幅、KPI 指標卡片、各州網格、GIS 地圖與增長趨勢圖全數正常顯示與對齊！
- **多檔案同步**：`index.html`、`live_page.html` 與 `live_page_utf8.html` 均完美同步生成！
