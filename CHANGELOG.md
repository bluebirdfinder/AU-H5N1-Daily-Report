# Changelog - 澳洲 H5N1 Daily Update 專案變更歷史記錄

所有專案版本更新與重大變更均紀錄於此。

---

## [v2.5.2] - 2026-09-02

### 📺 介面與導航功能 (UI & Navigation Enhancements)
- **主頁頂部雙功能按鈕**：在 `index.html` 與 `report_template.html` 頂部 Sticky Header 新增 `📺 16:9 週報簡報 (Slides)` 與 `📂 歷次週報歸檔` 雙功能控制鈕。
- **歷次週報歸檔 Modal 彈窗 (`toggleArchiveModal()`)**：點擊按鈕跳出彈窗，可線上直接瀏覽並開啟 `weekly_reports/` 資料夾內所有歷史每週簡報。

### 🤖 Gemini AI 全網情報整合 (Gemini AI Grounding & Auto-Synthesis)
- **實時新聞與政策 AI 檢索 (`analyze_new_species_with_gemini()`)**：整合 Gemini API Google Search Grounding，自動搜尋 DAFF 未包含之新聞、各州政策（如 NSW DPIRD 海灘遛狗繫繩、後院養雞圈養）、離島撤離與哺乳類病例。
- **動態歸檔清單生成器 (`generate_dynamic_weekly_archive_html()`)**：在 `h5n1.py` 中自動掃描 `weekly_reports/` 資料夾，自動解析日期區間檔名並生成響應式 HTML 卡片供 Modal 彈窗調用。

### 📊 最新數據對齊 (Data Updates)
- 全澳確診事件總數同步至 **456 起**（一週內激增 +147 起）。
- 州別數據：南澳 267 起、維州 140 起、塔州 20 起、NSW 17 起、西澳 10 起、昆州 2 起。
- 商業家禽、蛋場與乳牛場維持 **100% 完美零確診 (Area Freedom)**。

---

## [v2.5.1] - 2026-09-02

### 📂 資料夾留檔機制 (Weekly Report Archiving)
- **建立 `weekly_reports/` 歷史週報歸檔資料夾**：
  - 每週自動留檔存檔簡報，檔名加入精確日期區間（例如：`weekly_reports/h5n1_weekly_report_20260824_20260902.html`）。

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
