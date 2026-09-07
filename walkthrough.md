# H5N1 定量風險評估、eBird 雙軌 GIS 數據整合與 CI/CD 修復 (v2.8.1)

已成功修復 **GitHub Actions CI/CD 自動化流程 (Exit status 128)**、完成 **eBird 雙軌 GIS 地圖圖層**、**零 CORS 阻擋靜態 JS 打包**、**當前月份動態對齊**、**英文版 eBird 看板同步**、**週報簡報歸檔解耦** 與 **全澳 484 起 DAFF 數據對齊**！

---

## 🌟 最新修復與完成重點 (v2.8.1 - 2026-09-07)

1. **🚀 GitHub Actions CI/CD 自動化流程修復 (`.github/workflows/auto_update.yml`)**
   - 修復 Step 5 `git add` 因找不到 `live_page_en.html` 導致 Exit code 128 報錯中斷的問題。
   - 於 Step 4b 加入英文版 Live 頁面自動複製備份指令 (`cp index_en.html live_page_en.html`)。
   - 完整將 4 大報告網頁 (`index.html`, `index_en.html`, `risk_assessment.html`, `risk_assessment_en.html`)、簡報檔 (`h5n1_weekly_slides.html`, `risk_assessment_slides.html`, `risk_assessment_slides_en.html`) 與 `weekly_reports/` 歸檔全數納入自動化追蹤。

2. **🦅 eBird 雙軌 GIS 地圖圖層與實測點位 (`risk_assessment.html` & `risk_assessment_en.html`)**
   - **實態野鳥觀測點位圖層 (`🦅 eBird 實態點位`)**：在 Leaflet 地圖上繪製全澳 129 筆亮青色脈衝圓圈點位，點擊或懸停可完整查閱物種 (`comName`)、地點 (`locName`)、實際目擊數量 (`howMany` 隻) 與觀測時間 (`obsDt`)。
   - **地圖節點 Tooltip 雙軌比對 (Model Projected vs eBird Observed)**：大候鳥停歇光圈（如莫頓灣 Moreton Bay、獵人河口 Hunter Estuary 等）懸停 Tooltip 同時呈現「📊 模型預估滯留量」與「🦅 eBird 30天周邊 220km 實測目擊數量與筆數」。

3. **⚡ 免 fetch 零 CORS 阻擋靜態打包 (`assets/js/bird_data.js`)**
   - `h5n1.py` 自動將 eBird 數據打包寫入 `assets/js/bird_data.js` (`window.ebirdDataEmbedded`)，徹底解決 Windows 本機檔案直接點開 (`file://`) 時瀏覽器跨域 `fetch` 阻擋造成的「載入中...」現象。

---

## 📸 實體驗證畫面

![GIS Dual-Track HUD & eBird Layer Screenshot](media_eab05364-982f-464b-8688-d4885a34aaff_1788748991863)

---

## 🚀 手動 Git Upload 上傳指令清單

請複製以下 Terminal 指令進行專案 Git 提交與推送：

```bash
git add .github/workflows/auto_update.yml live_page_en.html README.md CHANGELOG.md SOP.md task.md walkthrough.md
git commit -m "fix(ci): repair GitHub Actions workflow Exit code 128 error & sync live_page_en and documentation for v2.8.1 release"
git push origin main
```
