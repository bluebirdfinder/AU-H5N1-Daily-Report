# Changelog - 澳洲 H5N1 Daily Update 專案變更歷史記錄

所有專案版本更新與重大變更均紀錄於此。

---

## [v2.5.0] - 2026-09-02

### 🌟 新功能 (New Features)
- **16:9 Web Presentation Deck 網頁簡報系統 (`h5n1_weekly_slides.html`)**：
  - 新增 16:9 可簡報之網頁投影片，專為 2026.08.24 – 2026.09.02 澳洲 H5N1 核心疫情週報設計。
  - 支援鍵盤快速鍵導航 (`←`/`→`/`Space`/`PageUp`/`PageDown`/`Home`/`End`/`F 全螢幕`)。
  - 9 頁故事線結構，包含數據變化、陸海哺乳類失守（海豚與紅狐）、南極科學基地緊急撤離、金島企鵝暴斃、新州防範指引與 16:9 每週趨勢動態圖表。

### 🐛 錯誤修復 (Bug Fixes)
- **疫情週次增長趨勢圖表時間軸修復 (Weekly Epi-Curve Fix)**：
  - 修復 `report_template.html` 與 `index.html` 每週長條圖 (`eventTrendChart`) 寫死標籤止於 `8月W2` 導致 8月W3、8月W4、8月W5 與 9月W1 確診數據無法顯示且造成 8月W1 數據異常膨脹的問題。
  - 實作 `generateWeekLabels()` 動態時間軸生成器，自動擴充 X 軸標籤至當前最新週次 (`9月W1`)。

### 📊 數據更新 (Data Updates)
- 全澳確診事件總數升至 **446 起**（一週內激增 +137 起）。
- 州別數據：南澳 260 起、維州 138 起、塔州 20 起、NSW 16~17 起、西澳 10 起、昆州 2 起。
- 商業家禽、蛋場與乳牛場維持 **100% 完美零確診 (Area Freedom)**。

---

## [v2.0.0] - 2026-08-18

### 🌟 新功能 (New Features)
- **雙層獨立版塊架構 (Dual-Section Architecture)**：
  - 上半部：最新事件導向 (Event-Based Reporting) 即時動態監測專區。
  - 下半部：歷史隻數 (236 隻) 完整凍結資料庫專區。
- **Gemini Google Search Grounding 實時新聞與物種分析**：
  - 整合 Gemini API 自動搜尋最新媒體新聞與全新物種生態屬性。

---

## [v1.0.0] - 2026-08-12

### 🌟 初始版本 (Initial Release)
- 建立 Python 自動化爬蟲 `h5n1.py` 與 Leaflet GIS 地圖。
- 監控 Nestlé Purina Blayney 工廠地緣風險。
