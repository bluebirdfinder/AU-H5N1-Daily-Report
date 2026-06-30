# 澳洲 H5N1 疫情與 Nestlé Blayney 廠地緣風險自動化報告系統

本專案為獨立之澳洲 H5N1 禽流感疫情 GIS 自動更新報告系統。透過 GitHub Actions 每天自動爬取澳洲農業部 (DAFF) 官網最新數據，更新網頁 GIS 地圖，並自動部署發布於 GitHub Pages 上。

---

## 📂 檔案目錄結構
* **`h5n1.py`**：自動爬取澳洲農業部 (DAFF) 最新公告，更新病例資料庫，編譯輸出 `index.html` 的 Python 核心引擎。
* **`report_template.html`**：網頁 GIS 報告模板（整合 Leaflet.js 地圖與 Tailwind CSS 樣式，供 `h5n1.py` 讀取）。
* **`.github/workflows/auto_update.yml`**：GitHub Actions 定時自動化工作流設定檔（每天定時執行 2 次）。
* **`index.html`**：編譯後生成的正式報告網頁。

---

## ⚙️ 部署與架設指引

### 1. 建立獨立 GitHub 儲存庫 (Repository)
1. 前往您的 GitHub，建立一個**全新、獨立的儲存庫**，命名為 `AU_H5N1_Daily_Update`。
2. 將本資料夾內的所有檔案（包括 `.github` 資料夾、`h5n1.py`、`report_template.html` 與 `index.html`）以拖曳或 Git Push 上傳至該儲存庫中。

### 2. 啟用 GitHub Pages 網頁服務
1. 進入您在 GitHub 的 `AU_H5N1_Daily_Update` 專案頁面。
2. 點擊上方的 **`Settings` (設定) -> `Pages`**。
3. 在 **Build and deployment** 下的 **Source** 選擇 `Deploy from a branch`。
4. 在 **Branch** 選擇 `main`，路徑選擇根目錄 `/`，然後點擊 **Save** (儲存)。
5. 稍等約 1 分鐘，GitHub 會生成一個專屬的網址，點開即可瀏覽最新澳洲 H5N1 疫情地圖報告！

---

## 🕒 定時更新排程
本專案會自動在**每天早上 10:00** 和**傍晚 18:00 (台北時間)** 執行爬蟲，比對並更新 Roses Beach 案例與最新確診案例，重新編譯 `index.html` 並自動提交部署！
