# 任務清單與進度記錄 (Task Progress Record)

## 🟢 今日已完成重點 (2026-09-08 Completed - v2.9.0)
- [x] **🚨 NSW 確診激增至 22 起 · 攻入雪梨都會圈與瀕危物種數據更新 (`cases_events.json` & `h5n1.py`)**
  - [x] 納入雪梨北灘沃里伍德 (Warriewood, Northern Beaches Sydney) 與肯布拉港 (Port Kembla) 大鳳頭燕鷗首例確診點位。
  - [x] 納入科夫斯港 (Coffs Harbour) 全新南威爾斯州首例受脅瀕危留鳥「赫頓鸌 / 雪兒水鳥 (Hutton's Shearwater)」。
  - [x] 納入南海岸肖爾黑文 (Shoalhaven) 第 3 起海鳥群聚確診事件。
  - [x] 全澳確診事件總數同步至 **484 起** (SA 271, VIC 150, TAS 29, NSW 22, WA 10, QLD 2)，商業禽場維持 100% 零感染。

- [x] **🛡️ 全澳防疫政策、疫苗試驗與都會生物安全應變雷達 (Policy Radar Module)**
  - [x] 於中英文主頁 (`index.html` & `index_en.html`) 嵌入 4 欄式政策雷達看板（VIC 圈養令延長至 9/18 vs NSW 自願指引、阿德萊德紅狐都會警戒、Taronga Zoo 疫苗臨床試驗、BioResponse NSW App）。
  - [x] 擴充 `DEFAULT_SPECIES_PROFILES` 納入「赫頓鸌 (Hutton's Shearwater)」與「野生紅狐 (Red Fox)」生態屬性與風險指引。
  - [x] 病例明細表新增「🚨 新州 / 雪梨北灘 (NSW 22起)」與「🌊 赫頓鸌 / 瀕危留鳥 (科夫斯港)」一鍵快篩按鈕。

- [x] **⚖️ 定量風險模型同步 (`risk_assessment.html` & `risk_assessment_en.html`)**
  - [x] NSW 野生動物事件同步更新至 **22 起**。
  - [x] 重申 Blayney 廠與太平洋沿海突破點存在 >200km 距離與藍山山脈天然屏障，商業原料供應鏈維持安全。

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

