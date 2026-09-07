# H5N1 定量風險評估與 eBird 雙軌 GIS 數據整合改版 (v2.8.0)

已成功完成 **eBird 雙軌 GIS 地圖圖層與實態點位標註**、**零 CORS 阻擋靜態 JS 打包**、**當前月份動態對齊 (`new Date().getMonth()`)**、**英文版 eBird 看板同步**、**週報簡報歸檔解耦** 與 **全澳 484 起 DAFF 數據對齊**！

---

## 🌟 最新完成重點 (v2.8.0 - 2026-09-07)

1. **🦅 eBird 雙軌 GIS 地圖圖層與實測點位 (`risk_assessment.html` & `risk_assessment_en.html`)**
   - **實態野鳥觀測點位圖層 (`🦅 eBird 實態點位`)**：在 Leaflet 地圖上繪製全澳 129 筆亮青色脈衝圓圈點位，點擊或懸停可完整查閱物種 (`comName`)、地點 (`locName`)、實際目擊數量 (`howMany` 隻) 與觀測時間 (`obsDt`)。
   - **地圖節點 Tooltip 雙軌比對 (Model Projected vs eBird Observed)**：大候鳥停歇光圈（如莫頓灣 Moreton Bay、獵人河口 Hunter Estuary 等）懸停 Tooltip 同時呈現「📊 模型預估滯留量」與「🦅 eBird 30天周邊 220km 實測目擊數量與筆數」。
   - **地圖內 Top-Left 雙軌 HUD 儀表板**：實時呈現模型預估滯留總量 (2.2M AU / 600K NSW) vs eBird 近期實測數據 (129 筆觀測, 1,480+ 隻野鳥)。

2. **⚡ 免 fetch 零 CORS 阻擋靜態打包 (`assets/js/bird_data.js`)**
   - `h5n1.py` 自動將 eBird 數據打包寫入 `assets/js/bird_data.js` (`window.ebirdDataEmbedded`)，徹底解決 Windows 本機檔案直接點開 (`file://`) 時瀏覽器跨域 `fetch` 阻擋造成的「載入中...」現象，開檔即可順暢渲染。

3. **📅 當前月份動態對齊與面板切換**
   - 風險評估網頁改為依據系統當前日期 (`new Date().getMonth()`) 動態決定預設月分（9/7 開啟自動預設為 **9 月**），並提供 `[當前月份 (Sep)]` 與 `[🔥 10月 (年度高峰)]` 快捷按鈕。
   - 切換月份時，地圖 HUD 面板模型的預估滯留量與地圖熱點光圈隨之即時響應。

4. **🌐 疫情監控網頁英文版 eBird 組件同步 (`index_en.html` & `report_template_en.html`)**
   - 於 `report_template_en.html` 嵌入英文版 `eBird API v2 Live Field Sightings Feed` 即時遙測看板，編譯生成 `index_en.html`，達成疫情監控網頁中英文門戶 100% 雙語完全同步。

5. **📂 週報簡報歸檔與時間軸獨立解耦**
   - 疫情週報 (`h5n1_weekly_report_*.html`) 歸檔與風險評估簡報 (`risk_assessment_weekly_*.html`) 歸檔於各自網頁彈窗獨立呈顯。
   - 採 ISO 週一邊界演算法 (`YYYYMMDD_YYYYMMDD`) 計算檔案保存區間，徹底避免同週每日多餘測試檔殘留。

6. **📊 權威數據對齊 (DAFF 2026-09-07)**
   - 全澳確診事件總數同步至 **484 起**（包含 1,273 起排除案件與 34,358 筆熱線通報）。

---

## 📸 實體驗證畫面

![GIS Dual-Track HUD & eBird Layer Screenshot](media_eab05364-982f-464b-8688-d4885a34aaff_1788748991863)

---

## 🚀 手動 Git Upload 上傳指令清單

請複製以下 Terminal 指令進行專案 Git 提交與推送：

```bash
git add README.md CHANGELOG.md SOP.md task.md walkthrough.md h5n1.py cases_events.json report_template.html report_template_en.html index.html index_en.html risk_assessment.html risk_assessment_en.html bird_data.json assets/js/bird_data.js
git commit -m "docs & feat: release v2.8.0 with eBird dual-track GIS layers, zero-CORS JS bundle, dynamic month selection & DAFF 484 events alignment"
git push origin main
```
