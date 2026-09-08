# 任務清單與進度記錄 (Task Progress Record)

## 🟢 今日已完成重點 (2026-09-08 Completed - v2.9.5 & v2.9.4 & v2.9.3 & v2.9.2)
- [x] **🚨 確立最高指導原則：NSW 商業家禽場「零感染 (Area Freedom)」為唯一生死防線 (`AGENTS.md` / `AGENT.md`)**
  - [x] 明確建立最高指導原則：台灣檢疫法規以 NSW 全轄區為宣告單位，NSW 商業家禽場 0 確診是唯一的生死防線 (Red Line)。
  - [x] 嚴禁以距離 Blayney 廠單點公里數評估安全，全面校正為以 NSW 轄區整體防線與野鳥外溢威脅為核心。
- [x] **🦅 雙軌候鳥數據架構（推估總數 vs 現場實測總數）與 4 大候鳥源判讀指南**
  - [x] 清楚分離「📊 歷史季節模型【推估總數】(~50 萬隻先鋒 / NSW: ~6 萬隻)」與「🦅 現場實測【實際總數】(1,407 隻去重實測 / NSW: 286 隻)」。
  - [x] 全專案 6 份主頁與報告 HTML 嵌入 `💡 4 大候鳥數據源判讀指南` 互動式 Modal 彈窗。
- [x] **📊 2 年推演時間軸圖表重構（確診案件與候鳥數據全面解耦）**
  - [x] 官方確診事件數精確對齊 DAFF 官方即時統計（498 起，NSW 22 起），推演曲線自 2026.10 起銜接至 2028.06。
  - [x] 候鳥滯留量徹底分離「實地觀測統計 (18 萬隻)」與「季節模型推估 (50 萬隻先鋒至 220 萬隻峰值)」，消除當前點重複顯示問題。
- [x] **📺 16:9 簡報 Slide 4 候鳥數據補齊與全地圖「左側一體化極簡面板 (All-on-Left Compact HUD & Legend)」**
  - [x] Slide 4 頂部補齊 4 欄式生態 HUD 數據條（季節階段、歷史模型推估、現場實測總數、NSW 商業家禽威脅等級）。
  - [x] 地圖內部浮動 HUD 與航線圖例合併為左上角單一毛玻璃微型卡片（195px），徹底釋放 NSW、VIC、TAS、珊瑚海與塔斯曼海航線視野（100% 乾淨無遮擋）。
  - [x] 修復 1366×768 筆電解析度下內容高度溢出導致底部換頁按鈕被推擠問題，全螢幕與多解析度自適應常駐顯示。
- [x] **🌐 風險評估主網頁地圖同步升級 (`risk_assessment.html` & `risk_assessment_en.html`)**
  - [x] 風險評估主網頁地圖同步升級為左側一體化風控 HUD 與航線圖例面板。
- [x] **🧠 實裝 NSW 全轄區多因子數據科學加權矩陣 (Scientific Matrix)**
  - [x] 於 `risk_assessment.html` 與 `risk_assessment_en.html` 嵌入 4 欄式客觀加權剖析看板（NSW 商業防線、NSW 野鳥 ESI 嚴重度、鄰州逼近威脅、候鳥遙測水系暴露）。
  - [x] 內建 `autoAdjustRiskParameters()` 動態演算法，自動感應月份季節、遙測激增與官方事件對齊。
- [x] **🦅 候鳥多源數據全 HTML 自審 (Self-Audit) 與主頁 4 欄看板升級**
  - [x] 主頁與英文主頁升級為 Multi-Source Telemetry Hub (eBird + Movebank + GBIF + ALA)。
  - [x] 主頁 Leaflet 事件地圖正式疊加 Movebank 6 大候鳥衛星航跡圖層。
- [x] **🛰️ 全澳 6 大核心候鳥 Movebank 衛星發報器軌跡追蹤上線**
- [x] **🌐 GBIF 去重科研資料庫擴充至 17 大物種 (488 筆紀錄)**
- [x] **📂 每週雙週報獨立留檔與自動追補機制 (Weekly Auto-Archiving & Retroactive Catch-up)**
  - [x] 固定每週一 16:00 (AEST 18:00) 產出上一整週（上週一至本週一）統計。
  - [x] 自動於 `weekly_reports/` 另存含日期區間檔名（`h5n1_weekly_report_20260831_20260907.html`、`risk_assessment_weekly_20260831_20260907.html` 及英文版）。
  - [x] 實作智慧防呆週二追補，即使週一未開機，週二至週日執行均自動補做並歸檔。
- [x] **📱 16:9 簡報與風控儀表板 RWD 自適應與二行式標題排版升級**
  - [x] 頂部 Header 改採二行式結構（簡報標籤 + 週報週期 Badge + 主標題），徹底解決手機與小螢幕文字擠壓與折行問題。
  - [x] 手機端導航按鈕列導入 `whitespace-nowrap shrink-0` 與水平平滑捲動（`overflow-x-auto scrollbar-none`）。
- [x] **📊 疫情簡報核心數據與 NSW 破口全面對齊**
  - [x] 疫情簡報投影片 Slide 2、Slide 6、Slide 8 同步至全澳 484 起 (NSW 22 起，含雪梨北灘 Warriewood 大鳳頭燕鷗、肯布拉港、科夫斯港瀕危赫頓鸌)。
- [x] **🛡️ 企業資安白名單 CDN 全面替換 (Enterprise Whitelist CDN)**
  - [x] 全專案移除 `cdn.jsdelivr.net` 與 `unpkg.com`，全數替換為 `cdnjs.cloudflare.com`。
  - [x] 徹底解決雀巢企業內網與 Windows Defender IT 阻擋彈窗。

- [x] **⚖️ 定量風險模型現況校正 (`risk_assessment.html` & `risk_assessment_en.html`)**
  - [x] 維度 4 (NSW 疫情) 下拉選單預設校正為 `🟡 NSW 野鳥確診溫和增加 (20 ~ 50 起, 當前現況 22 起, 得分 35)`。
  - [x] 維度 3 (候鳥季節) 下拉選單預設校正為 `9 月：200 萬隻國際候鳥登陸 (當前現況, 得分 70)`。
  - [x] 雷達圖初始數據點對齊為 `[20, 70, 30, 35, 35]`，綜合評分對齊為 **37 分 (🟡 中風險緩衝)**。
  - [x] 重設模擬器 (`resetSimulator()`) 邏輯精準還原為當前現況。

- [x] **📺 16:9 雙語高階風險評估簡報 (`risk_assessment_slides.html` & `risk_assessment_slides_en.html`)**
  - [x] 具備 16:9 全螢幕投影、動態雷達圖、雙軸預測圖與資安白名單 CDN，並由 `h5n1.py` 於每週一自動歸檔至 `weekly_reports/`。

- [x] **🚨 NSW 確診激增至 22 起 · 攻入雪梨都會圈與瀕危物種數據更新 (`cases_events.json` & `h5n1.py`)**
  - [x] 納入雪梨北灘沃里伍德 (Warriewood, Northern Beaches Sydney) 與肯布拉港 (Port Kembla) 大鳳頭燕鷗首例確診點位。
  - [x] 納入科夫斯港 (Coffs Harbour) 全新南威爾斯州首例受脅瀕危留鳥「赫頓鸌 / 雪兒水鳥 (Hutton's Shearwater)」。
  - [x] 納入南海岸肖爾黑文 (Shoalhaven) 第 3 起海鳥群聚確診事件。
  - [x] 全澳確診事件總數同步至 **484 起** (SA 271, VIC 150, TAS 29, NSW 22, WA 10, QLD 2)，商業禽場維持 100% 零感染。

- [x] **🛡️ 全澳防疫政策、疫苗試驗與都會生物安全應變雷達 (Policy Radar Module)**
  - [x] 於中英文主頁 (`index.html` & `index_en.html`) 嵌入 4 欄式政策雷達看板（VIC 圈養令延長至 9/18 vs NSW 自願指引、阿德萊德紅狐都會警戒、Taronga Zoo 疫苗臨床試驗、BioResponse NSW App）。
  - [x] 擴充 `DEFAULT_SPECIES_PROFILES` 納入「赫頓鸌 (Hutton's Shearwater)」與「野生紅狐 (Red Fox)」生態屬性與風險指引。
  - [x] 病例明細表新增「🚨 新州 / 雪梨北灘 (NSW 22起)」與「🌊 赫頓鸌 / 瀕危留鳥 (科夫斯港)」一鍵快篩按鈕。

- [x] **📚 專案文檔與 SOP 同步**
  - [x] 更新 `README.md`、`CHANGELOG.md`、`GOVT_SCRAPING_BEST_PRACTICES.md`、`SOP.md`、`task.md`、`walkthrough.md`。

---

## 🟢 歷史已完成重點 (2026-09-07 Completed - v2.8.0 / v2.8.1)
- [x] **eBird 雙軌 GIS 地圖圖層與實態點位標註 (`risk_assessment.html` & `risk_assessment_en.html`)**
  - [x] 在 Leaflet 地圖上直接標註全澳 129 筆亮青色脈衝點位（`🦅 eBird 實態點位`）。
  - [x] 點擊與懸停點位顯示觀測物種、地點名稱、實際目擊數量與觀測日期。
  - [x] 地圖停歇點懸停 Tooltip 同時呈現「📊 模型預估滯留量」與「🦅 eBird 30天周邊 220km 實測目擊數量與筆數」。
  - [x] 地圖內 Top-Left 雙軌 HUD 面板即時對比模型預估值 vs eBird 近期實測數。

- [x] **⚡ 免 fetch 零 CORS 阻擋靜態打包 (`assets/js/bird_data.js`)**
  - [x] `h5n1.py` 自動將 eBird 觀測數據同步打包為 JS 檔案 (`window.ebirdDataEmbedded`)。
  - [x] 徹底解決 Windows 本機直接開啟 HTML (`file://`) 時瀏覽器跨域 `fetch` 阻擋問題，開檔即時流暢渲染。

- [x] **📅 當前月份動態對齊 (`new Date().getMonth()`)**
  - [x] 風險評估儀表板依據系統日期動態決定預設月份（9 月開啟自動選取 9 月面板）。
  - [x] 提供 `[當前月份 (Sep)]` 與 `[🔥 10月 (年度高峰)]` 快捷按鈕供快速切換與對比。

- [x] **🌐 疫情監控網頁英文版 eBird 組件同步 (`index_en.html` & `report_template_en.html`)**
  - [x] 於 `report_template_en.html` 嵌入 `eBird API v2 Live Field Sightings Feed` 遙測看板。
  - [x] 執行 `python h5n1.py` 產出 `index_en.html`，完成中英文疫情門戶 100% 雙語同步。

- [x] **📂 週報簡報歸檔與時間軸獨立解耦**
  - [x] 疫情週報 (`h5n1_weekly_report_*.html`) 與風險評估簡報 (`risk_assessment_weekly_*.html`) 於各網頁彈窗獨立歸檔。
  - [x] ISO 週一邊界演算法 (`YYYYMMDD_YYYYMMDD`) 自動清理過期測試檔。

- [x] **📊 數據權威對齊 (DAFF 2026-09-07)**
  - [x] 全澳確診事件總數同步至 **484 起**（包含 1,273 起排除案件與 34,358 筆熱線通報）。

