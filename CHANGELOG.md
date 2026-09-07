# Changelog - 澳洲 H5N1 Daily Update 專案變更歷史記錄

所有專案版本更新與重大變更均紀錄於此。

## [v2.8.0] - 2026-09-07

### 🦅 eBird 雙軌 GIS 地圖圖層與實測點位 (`risk_assessment.html` & `risk_assessment_en.html`)
- **實態野鳥觀測點位圖層 (`🦅 eBird 實態點位`)**：
  - 於 Leaflet 地圖上直接繪製全澳 129 筆亮青色脈衝圓圈點位，點擊或懸停可完整查閱物種 (`comName`)、地點 (`locName`)、實際目擊數量 (`howMany` 隻) 與觀測時間 (`obsDt`)。
- **地圖節點 Tooltip 雙軌比對 (Model Projected vs eBird Observed)**：
  - 大候鳥停歇光圈（如莫頓灣 Moreton Bay、獵人河口 Hunter Estuary 等）懸停 Tooltip 同時呈現「📊 模型預估滯留量」與「🦅 eBird 30天周邊 220km 實測目擊數量與筆數」。
- **地圖內 Top-Left 雙軌 HUD 儀表板**：
  - 實時呈現模型預估滯留總量 (2.2M AU / 600K NSW) vs eBird 近期實測數據 (129 筆觀測, 1,480+ 隻野鳥)。

### ⚡ 免 fetch 零 CORS 阻擋靜態打包 (`assets/js/bird_data.js`)
- `h5n1.py` 自動將 eBird 數據打包寫入 `assets/js/bird_data.js` (`window.ebirdDataEmbedded`)，徹底解決 Windows 本機檔案直接點開 (`file://`) 時瀏覽器跨域 `fetch` 阻擋造成的「載入中...」現象，開檔即可順暢渲染。

### 📅 當前月份動態對齊與面板切換
- 風險評估網頁改為依據系統當前日期 (`new Date().getMonth()`) 動態決定預設月分（例如 9/7 開啟自動預設為 **9 月**），並提供 `[當前月份 (Sep)]` 與 `[🔥 10月 (年度高峰)]` 快捷按鈕。
- 切換月份時，地圖 HUD 面板模型的預估滯留量與地圖熱點光圈隨之即時響應。

### 🌐 疫情監控網頁英文版 eBird 組件同步 (`index_en.html` & `report_template_en.html`)
- 於 `report_template_en.html` 嵌入英文版 `eBird API v2 Live Field Sightings Feed` 即時遙測看板，編譯生成 `index_en.html`，達成疫情監控網頁中英文門戶 100% 雙語完全同步。

### 📂 週報簡報歸檔與時間軸獨立解耦
- 疫情週報 (`h5n1_weekly_report_*.html`) 歸檔與風險評估簡報 (`risk_assessment_weekly_*.html`) 歸檔於各自網頁彈窗獨立呈顯。
- 採 ISO 週一邊界演算法 (`YYYYMMDD_YYYYMMDD`) 計算檔案保存區間，徹底避免同週每日多餘測試檔殘留。

### 📊 權威數據對齊 (DAFF 2026-09-07)
- 全澳確診事件總數同步至 **484 起**（包含 1,273 起排除案件與 34,358 筆熱線通報）。

---

## [v2.7.0] - 2026-09-04

### 🦅 野鳥與候鳥生態即時 API 整合 (eBird API v2 & ALA Backup)
- **eBird API v2 實時數據串接 (`fetch_ebird_data()`)**：
  - 透過 GitHub Secret (`EBIRD_API_KEY`) 安全注入，Server-side 爬取全澳 6 州（NSW、SA、WA、VIC、QLD、TAS）近 30 天內高風險水鳥與候鳥觀測紀錄。
  - 成功過濾 129 筆高風險物種目擊（銀鷗、鳳頭燕鷗、太平洋黑鴨、鸕鶿、蒼鷺等），輸出靜態 `bird_data.json`，金鑰永不外洩於前端。
- **Atlas of Living Australia (ALA) 免 Key 數據備援 (`fetch_ala_data()`)**：
  - 整合 `biocache.ala.org.au` REST API 檢索全澳 35,000+ 個生態調查點（含 Birdata、iNaturalist AU、澳洲博物館等），生成 `ala_bird_data.json`。
- **四層全維度數據備援體系 (4-Tier Data Fallback System)**：
  - **Tier 1 (主要官方)**：DAFF 官網 `curl_cffi` 擬真爬蟲與 Playwright WAF 繞過。
  - **Tier 2 (即時新聞)**：Google News RSS 動態關鍵字新聞流。
  - **Tier 3 (本地數據庫)**：`cases_events.json` 468+ 起歷史事件與自動補全對齊演算法。
  - **Tier 4 (生態 API)**：eBird API + ALA 生態資料庫實時動態。

### 📐 定量風險評估儀表板與排版優化 (`risk_assessment.html` & `risk_assessment_en.html`)
- **重返時間軸估算標籤更正**：將重返視窗估算器（Re-entry Window Estimator）中容易混淆的「6 階段 / 6-Stage」標籤更正為「3 情境 / 3-Scenario」（最樂觀 45 天、基準 90 天、極端 180 天）。
- **標頭換行適配**：在「模型/Model」前加入 `<br>` 換行，改善中英文版頂部視覺對稱性。

### 📊 最新權威數據對齊 (DAFF 2026-09-04)
- 全澳確診事件總數同步至 **468 起**（包含自動完成之 SA +1、VIC +5、NSW +4、TAS +2 案件對齊）。
- 州別數據：南澳 263 起、維州 148 起、塔州 25 起、NSW 20 起、西澳 10 起、昆州 2 起。
- 商業家禽、蛋場與乳牛場維持 **100% 完美零確診 (Area Freedom)**。

---

### 🗓️ 候鳥遷徙時間軸卡片 (Migratory Bird Seasonal Risk Timeline)
- **補回並獨立升級「候鳥遷徙回澳洲時間軸與高風險期動態評估」專區**：在 `report_template.html` 與 `index.html` 的「受影響野生鳥類物種與生態生物安全指南」專區內，補回 4 階段時間軸評估卡片：
  - **8 月下旬 (前鋒期)**：成年海鳥 (棕賊鷗/巨鸌) 前鋒抵達，造成目前全澳確診爆發與海獅/海豚感染。
  - **9 月 (☠️ 極高風險起點)**：200 萬隻、36 種國際候鳥大部隊正式登陸澳洲北部。
  - **10 月 (🔴 全國疫情地雷期)**：候鳥群自北部向全澳洲內陸溼地、灌木叢及東南沿海 (NSW/VIC/SA) 大規模分散。
  - **11 月~隔年 2 月 (高峰停留期)**：候鳥群留留在各地過冬覓食，至隔年 3 月集體北返。

---

### 📺 介面與導航功能 (UI & Navigation Enhancements)
- **主頁頂部雙功能按鈕**：在 `index.html` 與 `report_template.html` 頂部 Sticky Header 新增 `📺 16:9 週報簡報 (Slides)` 與 `📂 歷次週報歸檔` 雙功能控制鈕。
- **歷次週報歸檔 Modal 彈窗 (`toggleArchiveModal()`)**：點擊按鈕跳出彈窗，可線上直接瀏覽並開啟 `weekly_reports/` 資料夾內所有歷史每週簡報。

### 🤖 Gemini AI 全網情報整合與 404 Fallback 模型名稱修復 (Gemini AI Grounding & Bug Fix)
- **修復 Gemini API 404 模型無效報錯**：修復 GitHub Actions 紀錄中 `gemini-2.5-flash-lite` 與 `gemini-2.5-pro` 回傳 HTTP 404 找不到模型的錯誤，修正備援模型鏈為官方有效模型：`gemini-2.5-flash` ➔ `gemini-2.0-flash` ➔ `gemini-1.5-flash` ➔ `gemini-1.5-pro`。當主力模型遇 429 限流時可無縫切換備援模型。
- **實時新聞與政策 AI 檢索 (`analyze_new_species_with_gemini()`)**：整合 Gemini API Google Search Grounding，自動搜尋 DAFF 未包含之新聞、各州政策（如 NSW DPIRD 海灘遛狗繫繩、後院養雞圈養）、離島撤離與哺乳類病例。
- **動態歸檔清單生成器 (`generate_dynamic_weekly_archive_html()`)**：在 `h5n1.py` 中自動掃描 `weekly_reports/` 資料夾，自動解析日期區間檔名並生成響應式 HTML 卡片供 Modal 彈窗調用。

### 📊 最新數據對齊 (Data Updates)
- 全澳確診事件總數同步至 **456 起**（一週內激增 +147 起）。
- 州別數據：南澳 267 起、維州 140 起、塔州 20 起、NSW 17 起、西澳 10 起、昆州 2 起。
- 商業家禽、蛋場與乳牛場維持 **100% 完美零確診 (Area Freedom)**。

---

## [v2.6.0] - 2026-09-02

### ⚖️ H5N1 定量風險評估模型儀表板 (`risk_assessment.html`)
- **全新定量風險模型 (Quantitative Risk Score, 0 ~ 100 分)**：針對台灣團隊評估重啟澳洲 Nestlé Purina Blayney 廠寵物食品進口、擔憂 TW APHIA 宣告 NSW 為疫區之需求，建立 5 大維度動態權重算式：
  - $S_{housing}$ **政策與物理隔離 (25%)**：強制圈養令、物理防鳥網與水質消毒。
  - $S_{migratory}$ **候鳥遷徙與季節重疊 (20%)**：4 階段遷徙時間軸與 NSW 濕地水體重疊性。
  - $S_{vector}$ **跨物種傳播與哺乳類向量 (20%)**：南澳紅狐/海豚個案與陸生野生腐食動物夜間侵入禽舍風險。
  - $S_{virology}$ **病毒株傳播學 (15%)**：H5N1 Clade 2.3.4.4b 低溫耐受度、潛伏期 (1-3天) 與排毒量。
  - $S_{proximity}$ **地緣距離與商業零確診 (20%)**：全澳商業禽場 0 宗感染與距 Blayney 工廠 215 km 距離。
- **70/30 雙軌校準對照專區 (Dual-Track Calibration)**：
  - **全球 H5N1 Clade 2.3.4.4b 歐美經驗 (70%)**：判定病毒跨物種感染力與遠洋野鳥帶毒特性。
  - **澳洲本土 H7 歷史爆發軌跡 (30%)**：判定澳洲地理孤立性、州政府 2~4 週快封快切效率與 TW APHIA 歷史邊境封鎖慣例。
- **互動式敏感度模擬器 (Interactive Risk Simulator)**：內建 Chart.js 5 維度雷達圖 (Radar Chart)、參數下拉選單、商業禽場爆發開關與距離滑桿。

### 🌐 英文版全功能動態儀表板 (`index_en.html` & `report_template_en.html`)
- **英文獨立模板 (`report_template_en.html`)**：完整翻譯主儀表板所有專區、KPI 卡片、物種生態評估卡片、時間軸與表格欄位，專供寄送給國外同事與全球 Purina 團隊。
- **Python 自動化雙語編譯 (`h5n1.py`)**：每次執行連網抓取數據時，自動同時編譯產出 `index.html` (中文) 與 `index_en.html` (英文) 以及 `live_page_en.html`。
- **頂部 Header 導航切換**：在所有網頁頂部 Sticky Header 加入 `🌐 English Version` / `🌐 中文版` 與 `⚖️ Risk Model` 快速導航控制鈕。

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
