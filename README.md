# 澳洲 H5N1 疫情與 Nestlé Blayney 廠地緣風險自動化報告系統

本專案為獨立之澳洲 H5N1 禽流感疫情 GIS 自動更新報告系統。透過 GitHub Actions 每天自動爬取澳洲與地方政府官網及新聞 RSS 最新數據，結合地理編碼 API 自動更新網頁 GIS 地圖，並自動部署發布於 GitHub Pages 上。

---

## 🌟 核心功能特點
1. **全澳州聯防監控網絡與多重抗封鎖中繼陣列 (Cloudflare Worker & Multi-Proxy & Playwright & curl_cffi)**：同時爬取**澳洲聯邦農業部 (DAFF)** 以及**澳洲全部 8 個州/領地政府**的官方禽流感站點。導入多重抗封鎖架構：優先以 **Cloudflare Worker 代理**與 **`curl_cffi` Chrome TLS 指紋偽裝** 繞過機房 IP/WAF 阻擋，備有 **CodeTabs / ThingProxy / AllOrigins 多重跨域 Web Proxy** 與 **Playwright 真實瀏覽器**，並搭配 **Google News RSS 兜底**，確保數據 100% 不漏報、不中斷。
2. **智慧權威數據解析與全域精確去重**：直接從澳洲聯邦農業部 (DAFF) 官網解析權威確診隻數與事件數（123 隻確診 / 42 起事件），並實作中英文地名別名與 GPS 物理距離 (<15.0km) 雙重去重，徹底防止每日自動排程重複新增或暴增案例。
3. **AI 智慧地理定位與多段退避 (Nominatim API & Cloudflare Proxy)**：當新聞或官網出現全新疫情地點時，程式會自動使用 OpenStreetMap 地理編碼 API 查詢其精確 GPS 經緯度，並實作多段退避機制防止定位失敗，自動在網頁地圖上標示新病例。
4. **媒體確診交叉驗證 (C 方案)**：結合「主流媒體白名單」與「官方首長/國家實驗室發言人及確診詞」雙重過濾，自動將媒體報導的最新疫情於官方網站同步延遲期間內搶先升級，並於前端地圖與表格自動標示精緻的 **`⚠️ 媒體先行 (官網同步中)`** Badge，保證極高的時效性與數據真實性。
5. **動態最短距離計算 (Haversine 公式)**：自動計算各病例到 Blayney 廠的球體直線距離，並在網頁頂部標籤、地緣安全宣告、最下方三大黃金論點第 3 點等三處，自動更新為最新的最近距離。
6. **動態日期與情境摘要生成**：捨棄硬編碼，自動計算數據庫中最新確診日期並替換，且能根據近 3 日內有無新增案例自動切換「警報語氣」或「常態觀察平穩語氣」。
7. **自適應動態參考文獻庫**：底部的參考資料（References）完全動態生成，會根據當前數據庫中病例所分布的省份（如西澳 WA、維多利亞州 VIC），自動追加該省政府農業廳的官方監控網址。
8. **Playwright 瀏覽器截圖與 Gemini Vision AI 視覺自動辨識**：當政府官網 HTML 因阻擋或防火牆無法直接爬取時，系統會自動使用 Playwright 無頭 Chromium 瀏覽器開啟 DAFF 官網並拍攝高解析度全頁截圖，接著呼叫 **Gemini 2.0 Flash Vision API** 直接閱讀截圖中的文字與數據框，自動識別最新確診數字並同步至網頁，達到 100% 全自動零人工干預更新。
9. **雙時區對齊與陰性排除自動化**：最後編譯時間自動校正顯示台北時間與澳洲 AEST 時間，並實現陰性案例的自動識別與雙向狀態更新。

---

## 📂 檔案目錄結構
* **`cases.json`**：**獨立病例數據庫（數據與邏輯徹底解耦）**。存放歷史與即時更新的所有病例節點，爬蟲執行時自動載入並覆寫。
* **`h5n1.py`**：自動爬取官方與新聞 RSS，結合 Playwright 截圖與 Gemini Vision AI 視覺識別、自動定位新地點、執行權威對帳並編譯輸出 `index.html` 的 Python 核心引擎。
* **`report_template.html`**：網頁 GIS 報告模板（整合 Leaflet.js 地圖、Tailwind CSS 樣式、鳥類數量密度動態 Badge 圈圈、雷達水波光圈與專屬金色 🏭 Nestlé Blayney 工廠地標）。
* **`GOVT_SCRAPING_BEST_PRACTICES.md`**：**政府公開資料爬取與抗封鎖架構開發經驗指南**（供未來開發其他政府數據專案參考）。
* **`.github/workflows/auto_update.yml`**：GitHub Actions 定時自動化工作流設定檔（每天定時執行 2 次，自動觸發 Playwright+Gemini Vision 並 commit `index.html` 與 `cases.json`）。
* **`index.html`**：編譯後生成的正式報告網頁。
* **`live_page.html`** / **`live_page_utf8.html`**：同步生成之線上備用部署網頁。
* **`walkthrough.md`**：專案開發與 Bug 修正軌跡日誌。
* **`task.md`**：任務排程與完成度檢核表。
* **`更新說明`**：最後檔案同步日期更新於 2026-08-07 15:25 (完成 Playwright 瀏覽器截圖 + Gemini Vision AI 圖片讀字全自動化流程建置，並同步更新 2026-08-07 3pm AEST DAFF 最新官方數據：全澳累計 175 隻確診 / 49 起事件)。
