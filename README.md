# 澳洲 H5N1 疫情與 Nestlé Blayney 廠地緣風險自動化報告系統

本專案為獨立之澳洲 H5N1 禽流感疫情 GIS 自動更新報告與高階決策簡報系統。透過 GitHub Actions 每天自動爬取澳洲聯邦與地方政府官網及新聞 RSS 最新數據，結合地理編碼 API 自動更新網頁 GIS 地圖，並提供 16:9 網頁版簡報投影片與 GitHub Pages 自動部署發布。

---

## 🌟 核心功能特點 (Core Feature Matrix)

### 1. 📺 16:9 網頁版高階簡報系統 (`h5n1_weekly_slides.html`) **[2026-09-02 全新上線]**
- **16:9 簡報視覺適配**：採用現代黑暗科技美學與玻璃擬物風格 (Dark Slate Glassmorphism)，支援全螢幕簡報模式與 1080p/720p 視窗自適應居中縮放。
- **全功能簡報操控**：支援鍵盤方向鍵 (`←` / `→`)、`Space`、`PageUp` / `PageDown`、`Home` / `End` 及 `F` 鍵切換全螢幕，備有縮圖跳轉與進度條指示。
- **9 頁故事線精準呈現**：
  1. **Slide 1 封面**：2026.08.24 – 09.02 最嚴峻跨物種擴散期主題。
  2. **Slide 2 核心數據**：全國確診 309 ➔ 446 起 (+137起)、NSW 17 起、商業養殖場完美 0 確診。
  3. **Slide 3 重大突發 01**：陸海哺乳類全面失守（南澳首例海豚與陸生紅狐確診）。
  4. **Slide 4 重大突發 02**：南極 Macquarie Island 歷史性預防緊急撤離（24 名隊員）。
  5. **Slide 5 重大突發 03 & 04**：金島 100 隻神仙企鵝集體死亡 & 聯邦 DAFF 數據審核時間差。
  6. **Slide 6 NSW 現況**：Shoalhaven 新定點、南海岸區域控制、門迪迪湖鵜鶘排除 H5N1。
  7. **Slide 7 官方指引**：海灘遛狗強制繫繩、後院養雞 100% 室內圈養。
  8. **Slide 8 數據與趨勢**：左側數據摘要與各州細分 + 右側 16:9 Chart.js 互動式每週增長趨勢圖表 (Weekly Epi-Curve)。
  9. **Slide 9 簡報總結**：三大防線策略建議與返回封面控制。

### 2. 【上半部】最新「事件導向 (Event-Based Reporting)」即時動態監測專區
- **雙引擎 (Dual-Engine) AI 實時連網摘要**：整合 **Gemini API Google Search Grounding** 技術，主力模型採用 `gemini-3.6-flash`，自動連網搜尋當下最新澳洲 H5N1 報導，實時產出零時差情報摘要。
- **純事件計數規範**：對齊 DAFF 官方最新國際標準：**全澳 446 起確診事件 (Positive Events)**（截至 2026-09-02）、**1,273 起陰性排除事件** 與 **34,358 筆民眾與專家熱線通報**。
- **全澳 8 大州與行政區完整統計 (Events By Territory)**：
  - **南澳 (SA) 260 起**、**維州 (VIC) 138 起**、**塔州 (TAS) 20 起**、**新州 (NSW) 16 起 (初檢17起，Blayney 工廠同州)**、**西澳 (WA) 10 起**、**昆州 (QLD) 2 起**、**北領地 (NT) 0 起**、**首都區 (ACT) 0 起**。
- **100% 全動態 UI 渲染與週次圖表修正 (`generateWeekLabels()`)**：
  - 徹底解決舊版圖表寫死週次標籤止於 8 月 W2 的問題，改用 `generateWeekLabels()` 動態產生 6 月 W3 至 9 月 W1 時間軸，精確還原 8 月下旬至 9 月初（8月 W3 104起、9月 W1 135起）野鳥爆發高峰。
- **野生動物與物種生態指南 (Species Bio-Security Guide)**：
  - **物種圓餅圖 (`speciesDonutChart`)**：解析大鳳頭燕鷗 (317起)、銀鷗/海鷗 (60起)、巨鸌類 (55起)、太平洋鷗 (4起)、棕賊鷗 (3起)、黑面鸕鶿 (2起)、小企鵝 (1起)、遊隼與其它物種 (4起)。
  - **8 大主要物種深度生態與生物安全評估卡片**。
- **⚡ 多段跨障礙 HTTP 抓取器 (`smart_fetch_url` + Playwright `set_content`)**：採用 `curl_cffi` 擬真 Chrome 124 TLS 指紋，極速繞過 Cloudflare/Akamai WAF，Playwright 本地 0.1 秒渲染截圖。

### 3. 【中間區塊】DAFF 數據規範切換告示欄 (Policy Transition Notice)
- 標註生效時間：**2026 年 8 月 12 日 19:00 AEST (台北時間 2026-08-12 17:00)**。
- 說明 DAFF 改採國際標準「確診事件導向」背景，下半部歷史隻數庫完整封存。

### 4. 【下半部】歷史隻數 (236 隻) 完整凍結資料庫專區 (Frozen Historical Section)
- 完整紀錄自 2024 年 11 月首例爆發至 2026 年 8 月 12 日 17:00 AEST 官方凍結前之 **236 隻單鳥確診 / 55 起歷史個案**。

---

## ⏰ 排程自動更新機制 (Automated GitHub Actions Schedule)

配合澳洲聯邦農業部 (DAFF) 官方最新數據規範 **「每日 17:00 AEST 進行全澳數據結算」**，系統排程設為每日雙班次自動執行：
1. **主抓班次（台灣 16:00 / 澳洲 AEST 18:00 / 08:00 UTC）**：於 DAFF 17:00 AEST 結算發布後精準抓取最新數據。
2. **覆核與新聞班次（台灣 07:00 / 澳洲 AEST 09:00 / 23:00 UTC）**：隔日早晨覆核，即時捕捉各州政府官網與澳洲媒體 RSS (ABC News) 最新事件。

---

## 📜 版本歷史紀錄 (Version History & Changelog)

### v2.5 (2026-09-02)
- 🚀 **全新功能**：新增 16:9 Web 簡報網頁 `h5n1_weekly_slides.html`，提供 9 頁高階報告投影片、全螢幕播放、鍵盤導航與動態 Chart.js 增長趨勢圖表。
- 🐛 **重要 Bug 修復**：修復 `report_template.html` 與 `index.html` 每週疫情長條圖 (`eventTrendChart`) 寫死週次標籤止於 `8月W2` 的問題，改用 `generateWeekLabels()` 動態擴充標籤至 `9月W1`，消除 8月W1 數據異常膨脹。
- 📊 **數據更新**：全澳 H5N1 確診事件更新至 **446 起** (單週激增 +137 起)，南澳 260 起、維州 138 起、塔州 20 起、NSW 16~17 起、西澳 10 起、昆州 2 起。
- 🛡️ **防衛事實**：全澳商業家禽、蛋場與乳牛場維持 **100% 完美零確診**。

### v2.0 (2026-08-18)
- 🚀 **架構重構**：導入 Event-Based Reporting 上下雙層獨立專區架構，區隔即時事件 (Event-Based) 與歷史隻數庫 (Bird-Based)。
- 🤖 **AI 升級**：導入 Gemini API Google Search Grounding 技術，實現實時新聞與新物種動態 AI 分析。

### v1.0 (2026-08-12)
- 🎉 **初始版本**：建立基本 H5N1 抓取引擎、Leaflet 地圖整合與 Blayney 工廠地緣隔離監控。

---

## 📂 檔案目錄結構

* **`h5n1_weekly_slides.html`**：**16:9 網頁版高階簡報投影片** (2026.08.24 – 09.02 週報決策簡報)。
* **`index.html`**：編譯後生成的正式動態報告網頁。
* **`report_template.html`**：雙層獨立版塊網頁 GIS 報告與動態週次圖表模板。
* **`h5n1.py`**：自動爬取官方與新聞 RSS，結合 `curl_cffi`、Playwright 截圖、Gemini Grounding AI 情報識別之核心 Python 引擎。
* **`cases_events.json`**：**動態事件資料庫** (446 起 Positive Events 點位與屬性紀錄)。
* **`cases.json`**：**歷史單鳥隻數資料庫** (236 隻凍結點位紀錄)。
* **`species_cache.json`**：物種生態與生物安全快取資料庫。
* **`live_page.html`** / **`live_page_utf8.html`**：同步生成之線上備用部署網頁。
* **`SOP.md`**：開發與發布標準作業程序 SOP。
* **`walkthrough.md`**：開發與改版驗證紀錄。
* **`task.md`**：任務排程與檢核表。
* **`GOVT_SCRAPING_BEST_PRACTICES.md`**：政府官網爬取安全最佳實踐指南。
