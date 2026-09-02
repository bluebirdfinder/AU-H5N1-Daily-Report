# 澳洲 H5N1 疫情與 Nestlé Blayney 廠地緣風險自動化報告系統

本專案為獨立之澳洲 H5N1 禽流感疫情 GIS 自動更新報告與高階決策簡報系統。透過 GitHub Actions 每天自動爬取澳洲聯邦 (DAFF) 與地方政府官網及新聞 RSS 最新數據，結合 Gemini AI Google Search Grounding 實時情報檢索，自動更新網頁 GIS 地圖，並提供 16:9 網頁版簡報投影片與歷次週報歸檔庫。

---

## 🌟 核心功能特點 (Core Feature Matrix)

### 1. 📺 16:9 網頁版高階簡報系統與歷次歸檔彈窗 (`weekly_reports/`) **[2026-09-02 全新升級]**
- **主頁 Sticky Header 直捷選單**：主頁 `index.html` 頂部嵌入 `📺 16:9 週報簡報 (Slides)` 與 `📂 歷次週報歸檔` 雙功能按鈕，無需登入 GitHub 找程式碼，點擊即可瀏覽。
- **歷次週報歸檔 Modal 彈窗 (`generate_dynamic_weekly_archive_html()`)**：點擊「歷次週報歸檔」開啟彈窗，系統自動動態掃描 `weekly_reports/` 資料夾，提供一鍵開啟各週歷史簡報連結（檔名含日期區間，如 `h5n1_weekly_report_20260824_20260902.html`）。
- **16:9 簡報視覺適配與全功能操控**：採用現代黑暗科技美學 (Dark Slate Glassmorphism)，支援鍵盤 (`←`/`→`/`Space`/`PageUp`/`PageDown`/`Home`/`End`/`F`) 與全螢幕簡報模式。
- **9 頁故事線精準呈現**：包含數據變化、陸海哺乳類失守（海豚與紅狐）、南極科學基地緊急撤離、金島企鵝暴斃、新州防範指引與 16:9 Chart.js 每週趨勢動態圖表。

### 2. 🤖 Gemini AI 全網情報整合 (DAFF + 各州政策 + 新聞 RSS + Gemini Search Grounding)
- **雙引擎 (Dual-Engine) AI 實時連網摘要**：整合 **Gemini 2.5/3.6 API Google Search Grounding** 技術，主動連網搜尋當下最新澳洲 H5N1 報導與地方政策，補足 DAFF 官網未提供之新聞與生物安全法規。
- **全自動注入週報**：Python 腳本將 DAFF 官方 456 起數據、各州 DPIRD 政策（如海灘遛狗繫繩、後院養雞圈養）與 Gemini AI 分析結果自動合成為 16:9 週報簡報並歸檔。
- **純事件計數規範**：對齊 DAFF 官方最新國際標準：**全澳 456 起確診事件 (Positive Events)**（截至 2026-09-02）、**1,273 起陰性排除事件** 與 **34,358 筆民眾與專家熱線通報**。
- **全澳 8 大州與行政區完整統計 (Events By Territory)**：
  - **南澳 (SA) 267 起**、**維州 (VIC) 140 起**、**塔州 (TAS) 20 起**、**新州 (NSW) 17 起 (Blayney 工廠同州)**、**西澳 (WA) 10 起**、**昆州 (QLD) 2 起**、**北領地 (NT) 0 起**、**首都區 (ACT) 0 起**。
- **100% 全動態 UI 渲染與週次圖表修正 (`generateWeekLabels()`)**：
  - 改用 `generateWeekLabels()` 動態產生 6 月 W3 至 9 月 W1 時間軸，精確還原 8 月下旬至 9 月初野鳥爆發高峰。

### 3. 【中間區塊】DAFF 數據規範切換告示欄 (Policy Transition Notice)
- 標註生效時間：**2026 年 8 月 12 日 19:00 AEST (台北時間 2026-08-12 17:00)**，宣示歷史隻數庫完整封存。

### 4. 【下半部】歷史隻數 (236 隻) 完整凍結資料庫專區 (Frozen Historical Section)
- 完整紀錄自 2024 年 11 月首例爆發至 2026 年 8 月 12 日 17:00 AEST 官方凍結前之 **236 隻單鳥確診 / 55 起歷史個案**。

---

## ⏰ 排程自動更新機制 (Automated GitHub Actions Schedule)

配合 DAFF 官方最新數據規範 **「每日 17:00 AEST 進行全澳數據結算」**，系統排程設為每日雙班次自動執行：
1. **主抓班次（台灣 16:00 / 澳洲 AEST 18:00 / 08:00 UTC）**：於 DAFF 17:00 AEST 結算發布後精準抓取最新數據，並於每週一自動歸檔週報。
2. **覆核與新聞班次（台灣 07:00 / 澳洲 AEST 09:00 / 23:00 UTC）**：隔日早晨覆核，即時捕捉各州官網與澳洲媒體 RSS 最新事件。

---

## 📜 版本歷史紀錄 (Version History & Changelog)

### v2.5.2 (2026-09-02)
- 📺 **主頁 UI 升級**：主頁 `index.html` 與 `report_template.html` 頂部新增 `📺 16:9 週報簡報` 與 `📂 歷次週報歸檔` 按鈕。
- 📂 **歷次歸檔 Modal 彈窗**：新增互動式歸檔彈窗，動態渲染 `weekly_reports/` 目錄內帶日期檔名之簡報連結。
- 🤖 **Gemini AI 自動情報整合**：整合 Gemini API Google Search Grounding 主動搜尋與合成非 DAFF 官網之新聞、各州政策與突發個案，自動注入週報。
- 📊 **最新數據對齊**：全澳 H5N1 確診事件更新至 **456 起** (單週激增 +147 起)，南澳 267 起、維州 140 起、塔州 20 起、NSW 17 起、西澳 10 起、昆州 2 起。

### v2.5.0 (2026-09-02)
- 🚀 **簡報系統**：新增 16:9 Web 簡報網頁 `h5n1_weekly_slides.html`，提供 9 頁高階報告投影片、全螢幕播放與 Chart.js 趨勢圖表。

### v2.0.0 (2026-08-18)
- 🚀 **雙層專區**：導入 Event-Based Reporting 上下雙層獨立專區架構，區隔即時事件與歷史隻數庫。

---

## 📂 檔案目錄結構

* **`weekly_reports/`**：**每週簡報留檔資料夾** (包含帶日期區間檔名之週報簡報，如 `h5n1_weekly_report_20260824_20260902.html`)。
* **`h5n1_weekly_slides.html`**：**16:9 網頁版高階簡報投影片** (最新週報主連結)。
* **`index.html`**：編譯後生成的正式動態報告網頁 (含週報歸檔 Modal 彈窗)。
* **`report_template.html`**：雙層獨立版塊網頁 GIS 報告與動態週次圖表模板。
* **`h5n1.py`**：自動爬取官方與新聞 RSS，結合 `curl_cffi`、Playwright 截圖、Gemini Grounding AI 情報識別與簡報歸檔之核心 Python 引擎。
* **`cases_events.json`**：**動態事件資料庫** (456 起 Positive Events 點位與屬性紀錄)。
* **`cases.json`**：**歷史單鳥隻數資料庫** (236 隻凍結點位紀錄)。
* **`SOP.md`**：開發與發布標準作業程序 SOP。
* **`walkthrough.md`**：開發與改版驗證紀錄。
* **`task.md`**：任務排程與檢核表。
* **`GOVT_SCRAPING_BEST_PRACTICES.md`**：政府官網爬取安全最佳實踐指南。
