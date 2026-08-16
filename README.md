# 澳洲 H5N1 疫情與 Nestlé Blayney 廠地緣風險自動化報告系統

本專案為獨立之澳洲 H5N1 禽流感疫情 GIS 自動更新報告系統。透過 GitHub Actions 每天自動爬取澳洲聯邦與地方政府官網及新聞 RSS 最新數據，結合地理編碼 API 自動更新網頁 GIS 地圖，並自動部署發布於 GitHub Pages 上。

---

## 🌟 核心功能特點 (雙層獨立版塊架構 Dual-Section Architecture)
系統全面採用 **「上下雙層完全獨立專區」** 設計，中間以醒目的 **2026-08-12 數據規範改版告示欄** 隔開：

### 1. 【上半部】最新「事件導向 (Event-Based Reporting)」即時動態監測專區
- **雙引擎 (Dual-Engine) AI 實時連網摘要**：整合 **Gemini API Google Search Grounding** 技術，自動主動連網搜尋當下最新澳洲 H5N1 媒體新聞與各州（如塔斯馬尼亞 TAS 首起棕賊鷗案例、維州與南澳最新動態），實時產出零時差的報導摘要。
- **純事件計數規範**：完全對齊 DAFF 官方最新國際標準：**全澳 236 起確診事件 (Positive Events)**（截至 2026-08-16）、**1,273 起陰性排除事件** 與 **21,041 筆民眾與專家熱線通報**。
- **全澳 8 大州與行政區完整統計 (Events By Territory)**：
  - 南澳 (SA) 166 起、維州 (VIC) 53 起、西澳 (WA) 10 起、新州 (NSW) 4 起（Blayney 工廠同州）、塔州 (TAS) 2 起、昆州 (QLD) 1 起、**北領地 (NT) 0 起**、**首都區 (ACT) 0 起**（已預先寫入支援未來自動辨識與定位）。
- **100% 全動態 UI 渲染 (`renderDynamicIndicators()`)**：所有 KPI 卡片、熱線說明、各州數據網格、GIS 地圖標題、事件明細表標題與數量 Badge 均由 JavaScript 動態寫入，零硬編碼過時殘留。
- **野生動物與物種生態指南 (Species Bio-Security Guide)**：
  - **DAFF 權威數據對齊物種圓餅圖 (`speciesDonutChart`)**：精確呈現大鳳頭燕鷗 (178起/75%)、銀鷗/海鷗 (28起/12%)、巨鸌類 (18起/7.6%)、太平洋鷗 (4起/1.7%)、棕賊鷗 (2起/0.8%)、黑面鸕鶿 (2起/0.8%)、小企鵝 (1起/0.4%)、遊隼與其它 (3起/1.3%) 之個案起數與百分比。
  - **8 大主要物種深度生態與生物安全評估卡片**：詳細標示候鳥/留鳥屬性、棲息習性、食物來源與對廠區供應鏈之風險層級說明（如銀鷗為 🔴 高風險向量、燕鷗為 🟠 大規模群聚爆發風險、棕賊鷗為 🟡 跨域長途向量、小企鵝/鸕鶿為 🟢 近海低風險、遊隼為 🟣 猛禽高空向量）。
  - **📱 垂直捲動彈性排版 (`max-h-[540px] overflow-y-auto`)**：卡片區塊獨立可滾動，手機與平板電腦均能順暢滑動瀏覽全部物種，不拉長頁面。
- **🤖 【Gemini API Google Search Grounding 實時新物種與哺乳類 AI 分析警示鏈】 (`analyze_new_species_with_gemini()` & `generate_gemini_grounded_summary()`)**：
  - 當 DAFF 數據中出現**全新物種**（鳥類或哺乳類，如黑天鵝 `Black swan`、鵜鶘 `Pelican`、塔斯馬尼亞惡魔 `Tasmanian Devil` 😈、紅狐狸 `Red Fox` 🦊、海獅 `Sea Lion` 🦭、狐蝠 `Flying Fox` 🦇 等），Python 腳本會**自動觸發 Gemini API + Google Search Grounding** 實時搜尋該物種在澳洲的生態屬性、候鳥/留鳥/哺乳類狀態、農場入侵性與生物安全風險層級，自動在網頁生成新物種卡片。
  - **🦭 哺乳類跨種傳播實時警示**：因應 DAFF 野鳥表格主要聚焦於野生鳥類監測，Gemini AI 在每日連網摘要時會**專門檢索全澳哺乳類動物（海豹、海獅、紅狐狸、野貓、塔斯馬尼亞惡魔等）的最新感染報導**，若發現異常死亡或感染病例，將自動於頂部「📰 媒體與生態監測風向」區塊以醒目粗體 Alert 特報提醒 Blayney 廠區加強生物安全防護。
- **🎯 100% 精確對齊 DAFF 全澳 236 起確診事件 (`EVENT-001` ~ `EVENT-236`)**：
  - 清理舊版 `CASE-001/002` 歷史測試雜訊，資料庫精確維護 236 起 DAFF 官方事件，表格 Badge 與看板 100% 精確呈現 `236 筆完整記錄`。
- **⚡ 前端一鍵動態快篩控制列 (Quick Filter Controls)**：
  - 移至地圖與表格之間，提供 `[全部 236 起]`、`[🏝️ 塔斯馬尼亞 (TAS)]`、`[🏭 新州 (NSW)]`、`[🔴 銀鷗/海鷗]`、`[🦅 棕賊鷗]`、`[🐧 小企鵝]` 一鍵點擊即時過濾。
- **數據來源透明標示**：頂部橫幅以 **綠色（即時官方數據）** 或 **橘色（備援預設值 / DAFF 連線異常）** 顯示，讓您一眼即可確認數字是否為真實爬取。

### 2. 【中間區塊】DAFF 數據規範切換告示欄 (Policy Transition Notice)
- 標註生效時間：**2026 年 8 月 12 日 19:00 AEST (台北時間 2026-08-12 17:00)**。
- 說明 DAFF 改採國際標準「確診事件導向」之背景原因，並宣示下半部歷史隻數庫完整封存告示。

### 3. 【下半部】歷史隻數 (236 隻) 完整凍結資料庫專區 (Frozen Historical Section)
- **歷史隻數基準點**：完整紀錄自 2024 年 11 月首例爆發至 2026 年 8 月 12 日 17:00 AEST 官方凍結前之 **236 隻單鳥確診 / 55 起歷史個案**（南澳 163 隻、維州 58 隻、西澳 10 隻、新州 4 隻、昆州 1 隻）。
- **獨立五大元件**：包含獨立之**歷史中文摘要、歷史隻數儀表板 (Bird KPIs)、歷史隻數週次累積圖 (`historicalBirdChart`)、歷史隻數點位與熱點地圖 (`historicalBirdMap`)、歷史 64 筆詳細病歷記錄表 (`historicalBirdTable`)**。

---

## ⏰ 排程自動更新機制 (Automated GitHub Actions Schedule)
配合澳洲聯邦農業部 (DAFF) 官方最新數據規範 **「每日 17:00 AEST 進行全澳數據結算」**，系統排程設為每日雙班次自動執行：
1. **主抓班次（台灣 16:00 / 澳洲 AEST 18:00 / 08:00 UTC）**：於 DAFF 17:00 AEST 結算並發布後 1 小時精準抓取最新國家級儀表板數據。
2. **覆核與新聞班次（台灣 07:00 / 澳洲 AEST 09:00 / 23:00 UTC）**：隔日早晨覆核，同時即時捕捉各州政府官網 (如 NSW DPIRD, VIC Agriculture Victoria, SA PIRSA, TAS Biosecurity) 與澳洲媒體 RSS (如 ABC News) 發布之最新事件與新聞。

---

## 🛡️ 數據品質與對齊防護機制 (Data Quality Safeguards)

| 防護層 | 函數 / 機制 | 說明 |
|:---:|:---|:---|
| 第一道 | `fetch_daff_updates()` | 永遠強制執行 DAFF 官網爬取，無跳過條件 |
| 第二道 | Playwright + `curl_cffi` | 雙擬真引擎克服 WAF / CORS 限制 |
| 第三道 | `analyze_new_species_with_gemini()` | Gemini Search Grounding AI 自動分析全新鳥類/哺乳類風險與生態 |
| 第四道 | `renderDynamicIndicators()` | 前端 DOM 100% 全動態渲染，徹底消除 HTML 寫死硬編碼殘留 |
| 第五道 | 雙軌異步地方先行機制 | 地方官網/媒體先行案例即時地圖標記 `⚠️ 媒體/地方先行`，DAFF 結算後自動升級 |
| 第六道 | `source` 透明標示 | 頂部橫幅顏色即時反映爬取狀態（綠=即時 / 橘=備援） |

---

## 📂 檔案目錄結構
* **`cases.json`**：**歷史單鳥隻數資料庫 (歷史 236 隻凍結點)**。封存截至 2026-08-12 17:00 AEST 官方凍結之 236 隻單鳥確診資料。
* **`cases_events.json`**：**動態事件資料庫 (2026-08-12 起即時追蹤)**。存放 236 起 Positive Events（截至 2026-08-16）與地方先行通報事件點位。
* **`species_cache.json`**：**物種生態與生物安全快取資料庫**。存放已由 Gemini AI 分析之 8 大物種屬性與評級。
* **`h5n1.py`**：自動爬取官方與新聞 RSS，結合 `curl_cffi`、Playwright 截圖、Gemini Grounding AI 情報識別與物種動態分析器，並編譯輸出 `index.html` 的 Python 核心引擎。
* **`report_template.html`**：雙層獨立版塊網頁 GIS 報告模板（包含動態物種生態卡片、物種環狀圖、一鍵快篩控制列）。
* **`index.html`**：編譯後生成的正式報告網頁。
* **`live_page.html`** / **`live_page_utf8.html`**：同步生成之線上備用部署網頁。
* **`walkthrough.md`**：專案開發與對齊重構軌跡日誌。
* **`task.md`**：任務排程與完成度檢核表。
* **`GOVT_SCRAPING_BEST_PRACTICES.md`**：政府官網爬取安全最佳實踐指南。
