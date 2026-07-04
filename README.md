# 澳洲 H5N1 疫情與 Nestlé Blayney 廠地緣風險自動化報告系統

本專案為獨立之澳洲 H5N1 禽流感疫情 GIS 自動更新報告系統。透過 GitHub Actions 每天自動爬取澳洲與地方政府官網最新數據，結合地理編碼 API 自動更新網頁 GIS 地圖，並自動部署發布於 GitHub Pages 上。

---

## 🌟 核心功能特點
1. **雙重官方監控網絡**：同時爬取**澳洲聯邦農業部 (DAFF)** 與**新南威爾斯州一次產業及區域發展廳 (NSW DPIRD)** 官網，獲取第一手的野鳥確診及疑似疫情。
2. **AI 智慧地理定位引擎 (Nominatim API)**：當官網出現全新疫情地點時，程式會自動使用 OpenStreetMap 地理編碼 API 查詢其精確 GPS 經緯度，自動在網頁地圖上標示新病例，實現 100% 免維護全自動定位。
3. **動態最短距離計算 (Haversine 公式)**：自動計算各病例到 Blayney 廠的球體直線距離，並在網頁頂部標籤、地緣安全宣告、最下方三大黃金論點第 3 點等三處，自動更新為最新的最近距離（實測 NSW Hawks Nest 距離為 289 公里），消除前後邏輯矛盾。
4. **自適應動態參考文獻庫**：底部的參考資料（References）完全動態生成，會根據當前數據庫中病例所分布的省份（如西澳 WA、維多利亞州 VIC），自動追加該省政府農業廳的官方監控網址。
5. **雙時區對齊**：最後編譯時間自動校正顯示台北時間與澳洲 AEST 時間。

---

## 📂 檔案目錄結構
* **`h5n1.py`**：自動爬取 DAFF 與 NSW DPIRD 官網，自動定位新地點並編譯輸出 `index.html` 的 Python 核心引擎。
* **`report_template.html`**：網頁 GIS 報告模板（整合 Leaflet.js 地圖與 Tailwind CSS 樣式，供 `h5n1.py` 讀取）。
* **`.github/workflows/auto_update.yml`**：GitHub Actions 定時自動化工作流設定檔（每天定時執行 2 次）。
* **`index.html`**：編譯後生成的正式報告網頁。
