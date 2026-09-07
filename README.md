# 澳洲 H5N1 疫情與 Nestlé Blayney 廠地緣風險自動化報告系統

本專案為獨立之澳洲 H5N1 禽流感疫情 GIS 自動更新報告與高階決策簡報系統。透過 GitHub Actions 每天自動爬取澳洲聯邦 (DAFF) 與地方政府官網及新聞 RSS 最新數據，結合 eBird API v2 與 Atlas of Living Australia (ALA) 全澳野鳥生態即時數據，以及 Gemini AI Google Search Grounding 實時情報檢索，自動更新網頁 GIS 地圖，並提供 16:9 網頁版簡報投影片與歷次週報歸檔庫。

---

## 🌟 核心功能特點 (Core Feature Matrix)

### 1. 🦅 野鳥與候鳥生態即時 API 整合 (eBird API v2 & ALA Backup) **[2026-09-04 全新升級]**
- **eBird API v2 實時數據串接**：透過 GitHub Secret (`EBIRD_API_KEY`) 安全注入，每日自動抓取全澳 6 州（NSW、SA、WA、VIC、QLD、TAS）近 30 天內高風險水鳥與候鳥觀測紀錄，輸出靜態 `bird_data.json`，金鑰永不外洩於前端。
- **Atlas of Living Australia (ALA) 免 Key 數據備援**：整合 `biocache.ala.org.au` REST API 檢索全澳 35,000+ 個生態調查點（含 Birdata、iNaturalist AU、澳洲博物館等），生成 `ala_bird_data.json`。
- **四層全維度數據備援體系 (4-Tier Data Fallback)**：
  - **Tier 1 (主要官方)**：DAFF 官網 `curl_cffi` 擬真爬蟲與 Playwright WAF 繞過。
  - **Tier 2 (即時新聞)**：Google News RSS 動態關鍵字新聞流。
  - **Tier 3 (本地數據庫)**：`cases_events.json` 468+ 起歷史事件與自動補全演算法。
  - **Tier 4 (生態 API)**：eBird API + ALA 生態資料庫實時動態。

### 2. ⚖️ 雙語定量風險評估模型儀表板 (`risk_assessment.html` & `risk_assessment_en.html`)
- **定量風險指標 (0 ~ 100 分)**：針對 Nestlé Purina Blayney 廠寵物食品進口安全建立 5 大維度加權算式（隔離防禦 25%、候鳥重疊 20%、向量傳播 20%、病毒學 15%、距離與商業零確診 20%）。
- **3 情境重返時間軸估算器 (3-Scenario Re-entry Estimator)**：提供最樂觀 45 天、基準 90 天、極端 180 天之廠區復工與進口重啟評估。
- **Audubon 風格粒子流動光軌與 12 個月候鳥動態 GIS 地圖**：結合 Leaflet 黑暗地圖與高精度 NSW 轄區邊界框選。

### 3. 📺 16:9 網頁版高階簡報系統與歷次歸檔彈窗 (`weekly_reports/`)
- **主頁 Sticky Header 直捷選單**：主頁 `index.html` 頂部嵌入 `📺 16:9 週報簡報 (Slides)` 與 `📂 歷次週報歸檔` 雙功能按鈕，點擊即可瀏覽。
- **歷次週報歸檔 Modal 彈窗 (`generate_dynamic_weekly_archive_html()`)**：自動掃描 `weekly_reports/` 資料夾，提供一鍵開啟各週歷史雙語簡報連結。
- **16:9 簡報視覺適配與全功能操控**：採用現代黑暗科技美學 (Dark Slate Glassmorphism)，支援鍵盤與全螢幕簡報模式。

### 4. 🤖 Gemini AI 全網情報整合 (DAFF + 各州政策 + 新聞 RSS + Gemini Search Grounding)
- **雙引擎 (Dual-Engine) AI 實時連網摘要**：整合 **Gemini 2.5/3.6 API Google Search Grounding** 技術，主動連網搜尋當下最新澳洲 H5N1 報導與地方政策。
- **純事件計數規範**：對齊 DAFF 官方最新國際標準：**全澳 468 起確診事件 (Positive Events)**（截至 2026-09-04）、**1,273 起陰性排除事件** 與 **34,358 筆熱線通報**。
- **全澳 8 大州與行政區完整統計 (Events By Territory)**：
  - **南澳 (SA) 263 起**、**維州 (VIC) 148 起**、**塔州 (TAS) 25 起**、**新州 (NSW) 20 起 (Blayney 工廠同州)**、**西澳 (WA) 10 起**、**昆州 (QLD) 2 起**、**北領地 (NT) 0 起**、**首都區 (ACT) 0 起**。

---

## ⏰ 排程自動更新機制 (Automated GitHub Actions Schedule)

配合 DAFF 官方最新數據規範 **「每日 17:00 AEST 進行全澳數據結算」**，系統排程設為每日雙班次自動執行：
1. **主抓班次（台灣 16:00 / 澳洲 AEST 18:00 / 08:00 UTC）**：於 DAFF 17:00 AEST 結算發布後精準抓取最新數據，並於每週一自動歸檔週報。
2. **覆核與新聞班次（台灣 07:00 / 澳洲 AEST 09:00 / 23:00 UTC）**：隔日早晨覆核，即時捕捉各州官網與澳洲媒體 RSS 最新事件。

---

### v2.8.1 (2026-09-07)
- 🚀 **GitHub Actions CI/CD 自動化流程修復與 4 大雙語頁面全覆蓋**：修復 `.github/workflows/auto_update.yml` 中 `git add` 因找不到 `live_page_en.html` 導致的 Exit status 128 中斷問題；於 Step 4b 補齊英文 Live 頁面備份，並將 4 大報告頁面、簡報檔 (`slides`) 與歸檔全數納入 CI/CD 自動推送機制。

### v2.8.0 (2026-09-07)
- 🦅 **eBird 雙軌 GIS 地圖圖層與實測點位**：於 Leaflet 地圖上直接標註 129 筆亮青色實態觀測點位（`🦅 eBird 實態點位`），Tooltip 支援顯示「📊 模型預估滯留量」與「🦅 eBird 30天周邊 220km 實測目擊數量與筆數」。
- ⚡ **零 CORS 阻擋靜態打包 (`assets/js/bird_data.js`)**：`h5n1.py` 自動將 eBird 觀測數據同步寫入 JS 檔 (`window.ebirdDataEmbedded`)，徹底解決 Windows 本機直接開啟 HTML (`file://`) 時遭遇的瀏覽器跨域 `fetch` 阻擋。
- 📅 **當前月份動態對齊 (`new Date().getMonth()`)**：風險評估網頁改依系統日期動態預設月份（9/7 開啟自動預設為 **9 月**），並提供 `[當前月份 (Sep)]` 與 `[🔥 10月 (年度高峰)]` 快捷按鈕。
- 🌐 **疫情監控網頁英文版 eBird 組件同步 (`index_en.html` & `report_template_en.html`)**：於英文版 Section 1 嵌入 `eBird API v2 Live Field Sightings Feed` 看板，達成中英文監控門戶 100% 雙語完全同步。
- 📂 **週報簡報歸檔與時間軸獨立解耦**：疫情動態週報歸檔與風險評估簡報歸檔於個別頁面獨立呈現，採用 ISO 週一邊界演算法 (`YYYYMMDD_YYYYMMDD`) 清理測試過期檔。
- 📊 **權威數據對齊**：對齊全澳 **484 起** 官方確診事件（DAFF 2026-09-07 最新結算）。

### v2.7.0 (2026-09-04)
- 🦅 **eBird API v2 野鳥數據整合**：實現 Server-side 爬取全澳 6 州近 30 天高風險水鳥/候鳥觀測，生成靜態 `bird_data.json`（Key 永不外洩）。
- 🌏 **Atlas of Living Australia (ALA) 免 Key 備援**：整合 `biocache.ala.org.au` API 作為生態數據第二備援源 (`ala_bird_data.json`)。
- 🛡️ **4 層全維度數據備援架構**：完成 Tier 1 (DAFF) + Tier 2 (RSS) + Tier 3 (`cases_events.json`) + Tier 4 (eBird & ALA) 防斷連體系。
- 📐 **3 情境估算器與 UI 校正**：將重返視窗估算器標籤更正為「3 情境 (3-Scenario)」，完成 `risk_assessment.html` 雙語排版換行修復。
- 📊 **確診事件同步**：對齊全澳 468 起官方確診事件。

### v2.6.0 (2026-09-02)
- ⚖️ **定量風險評估模型儀表板 (`risk_assessment.html` & `risk_assessment_en.html`)**：建置 5 大維度定量風險模型、Audubon 風格粒子流動地圖與 2 年雙軸時間軸圖表。

### v2.5.2 (2026-09-02)
- 📺 **主頁 UI 升級**：主頁 `index.html` 頂部新增 `📺 16:9 週報簡報` 與 `📂 歷次週報歸檔` 按鈕。

---

## 📂 檔案目錄結構

* **`weekly_reports/`**：**每週簡報留檔資料夾** (包含帶日期區間檔名之雙語週報簡報)。
* **`bird_data.json` / `assets/js/bird_data.js`**：**eBird API v2 高風險候鳥觀測資料庫與免 fetch 零阻擋 JS 包**。
* **`ala_bird_data.json`**：**Atlas of Living Australia 生態觀測備援資料庫**。
* **`risk_assessment.html` / `risk_assessment_en.html`**：**雙語 H5N1 定量風險評估模型儀表板**。
* **`h5n1_weekly_slides.html`**：**16:9 網頁版高階簡報投影片**。
* **`index.html` / `index_en.html`**：編譯後生成的正式雙語動態報告網頁。
* **`h5n1.py`**：自動爬取官方、新聞 RSS、eBird API 與 ALA API 之核心 Python 引擎。
* **`cases_events.json`**：**動態事件資料庫** (484 起 Positive Events 點位與屬性紀錄)。
* **`cases.json`**：**歷史單鳥隻數資料庫** (236 隻凍結點位紀錄)。
* **`SOP.md`**：開發與發布標準作業程序 SOP。
* **`walkthrough.md`**：開發與改版驗證紀錄。
* **`task.md`**：任務排程與檢核表。

