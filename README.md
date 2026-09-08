# 澳洲 H5N1 疫情與 Nestlé Blayney 廠地緣風險自動化報告系統

本專案為獨立之澳洲 H5N1 禽流感疫情 GIS 自動更新報告與高階決策簡報系統。透過 GitHub Actions 每天自動爬取澳洲聯邦 (DAFF) 與地方政府官網及新聞 RSS 最新數據，結合 eBird API v2 與 Atlas of Living Australia (ALA) 全澳野鳥生態即時數據，以及 Gemini AI Google Search Grounding 實時情報檢索，自動更新網頁 GIS 地圖，並提供 16:9 網頁版簡報投影片與歷次週報歸檔庫。

---

## 🌟 核心功能特點 (Core Feature Matrix)

### 1. 🦅 多源候鳥生態與衛星遙測追蹤整合 (eBird + Movebank + GBIF + ALA) **[2026-09-08 全新升級]**
- **4 大數據源無縫串接與零重複去重 (Zero-Duplicate Multi-Source Hub)**：
  - **eBird API v2 實態觀測**：每日自動抓取全澳 6 州近 30 天內高風險野鳥觀測紀錄（129 筆點位 / 1,407 隻實測）。
  - **Movebank 衛星發報器軌跡追蹤**：追蹤造訪澳洲之 6 大跨洋遷徙海鳥與涉禽（短尾水薙鳥、斑尾鷸、南方巨鸌、黑眉信天翁、紅腹濱鷸、大鳳頭燕鷗），高亮動態航線直接疊加於風控地圖與主頁 GIS 地圖。
  - **GBIF 全球生物多樣性去重科研庫**：擴充至 17 大高風險物種，排除 eBird 重複數據，補齊 488 筆 CSIRO 與博物館學術調查點位。
  - **Atlas of Living Australia (ALA)**：檢索全澳 35,000+ 個生態調查點作為免 Key 第三備援。
- **零 CORS 阻擋前端架構**：所有數據同步寫入 `assets/js/*.js`，Windows 本機 `file://` 離線開啟亦能瞬間載入圖資與航跡。

### 2. ⚖️ 雙語定量風險評估模型與數據驅動動態分級 (`risk_assessment.html` & `risk_assessment_en.html`)
- **候鳥數據動態感應自動分級 (Dynamic Risk Level Auto-Adjustment)**：
  - 依據當前月份（9月預設 70 分，10~11月自動躍升 90 分）與實時觀測數據（>3,000 隻自動動態升級）自動校正選單與指標，並標註「⚡ 數據即時連動」發光狀態。
  - 點擊「重設為當前現況」時自動依據實時數據演算法重設回最佳動態基準。
- **定量風險指標 (0 ~ 100 分)**：針對 Nestlé Purina Blayney 廠寵物食品進口安全建立 5 大維度加權算式（隔離防禦 25%、候鳥重疊 20%、向量傳播 20%、病毒學 15%、距離與商業零確診 20%）。
- **3 情境重返時間軸估算器 (3-Scenario Re-entry Estimator)**：提供最樂觀 45 天、基準 90 天、極端 180 天之廠區復工與進口重啟評估。

### 3. 📺 16:9 網頁版高階簡報系統與歷次歸檔彈窗 (`weekly_reports/`)
- **主頁 Sticky Header 直捷選單**：主頁 `index.html` 頂部嵌入 `📺 16:9 週報簡報 (Slides)` 與 `📂 歷次週報歸檔` 雙功能按鈕，點擊即可瀏覽。
- **歷次週報歸檔 Modal 彈窗 (`generate_dynamic_weekly_archive_html()`)**：自動掃描 `weekly_reports/` 資料夾，提供一鍵開啟各週歷史雙語簡報連結。
- **16:9 簡報視覺適配與全功能操控**：採用現代黑暗科技美學 (Dark Slate Glassmorphism)，支援鍵盤與全螢幕簡報模式。

### 4. 🛡️ 全澳防疫政策、疫苗試驗與都會生物安全應變雷達 (Policy Radar)
- **各州圈養令 (Housing Order) 雙軌追蹤**：維州 (VIC) 強制室內禁閉令延長 28 天至 2026/09/18；新州 (NSW) DPIRD 維持彈性自願性建議。
- **都會紅狐跨種感染都市警示**：阿德萊德都市野生紅狐染疫引發都會防線升級。
- **NSW 塔隆加動物園 (Taronga Zoo) 疫苗臨床試驗**：啟動瀕危/受脅野生鳥類 H5 疫苗試驗。
- **BioResponse NSW 前線野外公務員專用 App**：新州國家公園管理員專用應變 App，提供 24hr 動物疾病緊急專線 (`1800 675 888`)。

### 5. 🤖 Gemini AI 全網情報整合 (DAFF + 各州政策 + 新聞 RSS + Gemini Search Grounding)
- **純事件計數規範**：對齊 DAFF 官方最新國際標準：**全澳 498 起確診事件 (Positive Events)**、**2,450 起陰性排除事件** 與 **36,800 筆熱線通報**。
- **商業禽場維持 100% 零感染**：全澳所有商業家禽、蛋場、乳牛與豬場維持「0 確診」完美防線 (Area Freedom Status)。

---

## ⏰ 排程自動更新機制 (Automated GitHub Actions Schedule)

配合 DAFF 官方最新數據規範 **「每日 17:00 AEST 進行全澳數據結算」**，系統排程設為每日雙班次自動執行：
1. **主抓班次（台灣 16:00 / 澳洲 AEST 18:00 / 08:00 UTC）**：於 DAFF 17:00 AEST 結算發布後精準抓取最新數據，並於每週一自動歸檔週報。
2. **覆核與新聞班次（台灣 07:00 / 澳洲 AEST 09:00 / 23:00 UTC）**：隔日早晨覆核，即時捕捉各州官網與澳洲媒體 RSS 最新事件。

---

### v2.9.5 (2026-09-08)
- 🚨 **確立最高指導原則：NSW 商業家禽場「零感染 (Area Freedom)」為唯一生死防線 (`AGENTS.md`)**：
  - 確立台灣動植物防疫檢疫署 (BAPHIQ) 以「州轄區」為疫區宣告單位，嚴禁以「距離工廠公里數」模糊焦點，風險評估錨定於「逼近 NSW 州界」與「NSW 野鳥外溢至商業禽舍風險」。
- 🦅 **雙軌候鳥數據架構（推估總數 vs 現場實測總數）與 4 大候鳥源判讀指南**：
  - 清晰分軌呈現：**📊 歷史季節模型【推估總數】(~50 萬隻先鋒 / NSW: ~6 萬隻)** vs **🦅 現場實測【實際總數】(1,407 隻去重實測 / NSW: 286 隻)**。
  - 全專案 HTML 新增 `💡 4 大候鳥數據源判讀指南` 互動彈窗（eBird, Movebank, GBIF, ALA）。
- 📊 **2 年推演時間軸圖表重構（確診案件與候鳥數據全面解耦）**：
  - 確診案件即時對齊 DAFF 官方 498 起（NSW 22 起），候鳥數據分離「實地觀測統計 (18 萬隻)」與「季節模型推估 (50 萬隻先鋒至 220 萬隻峰值)」。
- 📺 **16:9 簡報 Slide 4 候鳥數據補齊與全地圖「左側一體化極簡面板」**：
  - Slide 4 補齊 4 欄式生態 HUD 數據條；地圖浮動視窗與圖例整合至左上角（195px），徹底釋放 NSW、VIC、TAS、珊瑚海與塔斯曼海航線視野（100% 乾淨無遮擋）。
  - 修復 1366×768 筆電解析度下底部換頁按鈕溢出問題，全螢幕與多解析度自適應常駐顯示。
- 🌐 **風險評估主網頁地圖同步升級**：`risk_assessment.html` 與 `risk_assessment_en.html` 同步升級為左側一體化風控 HUD 與圖例面板。

### v2.9.4 (2026-09-08)
- 🦅 **全專案 13 份 HTML 檔案候鳥遙測數據全面自審 (Self-Audit) 與同步**：
  - 主頁與英文主頁升級為 4 欄式多源候鳥生態與衛星遙測追蹤看板 (eBird + Movebank + GBIF + ALA)。
  - 主頁 Leaflet 疫情事件地圖全面疊加 Movebank 6 大候鳥衛星航跡圖層。
- ⚙️ **候鳥數據驅動之風險評估動態分級機制 (Dynamic Auto-Adjustment)**：
  - 於雙語風控模型中內建 `autoAdjustRiskParameters()`，自動感測 9 月 (70分) 與 10~11月高峰 (90分)，並具備實測鳥數激增 (>3000隻) 觸發自動動態升級機制，重設按鈕自動回復動態基準。

### v2.9.3 (2026-09-08)
- 🛰️ **全澳 6 大核心候鳥/海鳥 Movebank 衛星發報器軌跡追蹤引擎上線**：
  - 完整涵蓋造訪澳洲之 6 大跨洋遷徙海鳥（短尾水薙鳥、斑尾鷸、南方巨鸌、黑眉信天翁、紅腹濱鷸、大鳳頭燕鷗）。
  - 自動透過 GitHub Secrets (`MOVEBANK_USER`, `MOVEBANK_PASSWORD`) 授權讀取，生成零 CORS 阻擋之 `assets/js/movebank_tracks.js`，於風控地圖上動態呈現發報航跡。
- 🌐 **GBIF 全球科研與海洋科考去重資料庫擴充至 17 大物種**：
  - 排除 eBird 重複數據，補齊 **488 筆** CSIRO 國家科考船與博物館學術級調查紀錄 (`gbif_bird_data.json`)。

### v2.9.2 (2026-09-08)
- 📂 **每週雙週報獨立留檔與自動追補機制 (Weekly Auto-Archiving & Retroactive Catch-up)**：
  - 週報排程固定於每週一（Monday）16:00 台灣時間（AEST 18:00 DAFF 每日數據結算後）產出，自動於 `weekly_reports/` 另存包含日期區間之獨立檔案（`h5n1_weekly_report_YYYYMMDD_YYYYMMDD.html` 與雙語 `risk_assessment_weekly_*.html`）。
  - 內建週二至週日自動防呆追補，自動錨定前一整週週期（`2026.08.31 – 2026.09.07`），確保歷史檔案無縫留檔。
- 📱 **16:9 簡報與儀表板 RWD 自適應與二行式標題排版升級**：
  - 頂部導航採用二行式佈局（簡報標籤 + 日期區間 Badge + 主標題），徹底解決手機與小螢幕文字擠壓問題。
  - 手機端導航按鈕列支援橫向滑動（`whitespace-nowrap shrink-0` 與 `overflow-x-auto`），大幅提升行動端閱讀體驗。
- 📊 **簡報核心數據與 NSW 疫情全面同步**：
  - 簡報各頁（Slide 2、Slide 6、Slide 8）與風險評估模型全面同步至全澳 **484 起** (NSW 22 起，含雪梨北灘 Warriewood、肯布拉港、科夫斯港瀕危赫頓鸌)，商業禽舍維持 100% 零感染。

### v2.9.1 (2026-09-08)
- 🛡️ **企業資安白名單 CDN 全面替換 (Enterprise Whitelist CDN Compliance)**：
  - 全面將 `Chart.js` 與 `Leaflet` 圖資庫替換為 **Cloudflare Enterprise CDN (`cdnjs.cloudflare.com`)**，徹底杜絕雀巢公司電腦與 Windows Defender 彈出 `cdn.jsdelivr.net` / `unpkg.com` 之 IT 阻擋警示。
- ⚖️ **風險評估模擬器預設值與雷達圖校正 (`risk_assessment.html` & `risk_assessment_en.html`)**：
  - NSW 野鳥確診事件下拉選單校正為「`🟡 NSW 野鳥確診溫和增加 (20 ~ 50 起, 當前現況 22 起, 得分 35)`」，候鳥季節階段校正為「`9 月 (200 萬隻登陸, 得分 70)`」，雷達圖初始分數對齊為 **37 分 (🟡 中風險緩衝)**。
- 📺 **16:9 雙語風險評估簡報 (`risk_assessment_slides.html` & `risk_assessment_slides_en.html`) 正式納入部署**：
  - 完整支援 16:9 簡報投影、中英文雙向切換、動態雷達圖互動與每週一自動歸檔至 `weekly_reports/`。

### v2.9.0 (2026-09-08)
- 🚨 **NSW 確診激增至 22 起 · 病毒首度攻入雪梨都會圈 (Sydney Metro Breach)**：
  - 納入雪梨北灘沃里伍德 (Warriewood, Northern Beaches Sydney) 與肯布拉港 (Port Kembla) 大鳳頭燕鷗首例確診點位。
  - 納入科夫斯港 (Coffs Harbour) 全新南威爾斯州首例受脅瀕危留鳥物種「赫頓鸌 / 雪兒水鳥 (Hutton's Shearwater)」。
  - 納入南海岸肖爾黑文 (Shoalhaven) 第 3 起海鳥群聚確診事件。
- 🛡️ **全澳防疫政策、疫苗試驗與都會生物安全應變雷達 (Policy Radar Module)**：
  - 於中英文主頁 (`index.html` & `index_en.html`) 嵌入 4 欄式政策雷達看板（VIC 圈養令延長至 9/18 vs NSW 自願指引、阿德萊德紅狐都會警戒、Taronga Zoo 疫苗臨床試驗、BioResponse NSW App）。
- 🦅 **物種生態庫擴充與一鍵快篩強化**：
  - `DEFAULT_SPECIES_PROFILES` 擴充「赫頓鸌 (Hutton's Shearwater)」與「野生紅狐 (Red Fox)」生態屬性與風險指引。
  - 病例明細表新增「🚨 新州 / 雪梨北灘 (NSW 22起)」與「🌊 赫頓鸌 / 瀕危留鳥 (科夫斯港)」一鍵快篩按鈕。
- ⚖️ **定量風險模型同步 (`risk_assessment.html` & `risk_assessment_en.html`)**：
  - NSW 野生動物事件同步更新至 **22 起**，重申 Blayney 廠與太平洋沿海突破點存在 >200km 距離與藍山山脈天然屏障，商業原料供應鏈維持安全。

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

