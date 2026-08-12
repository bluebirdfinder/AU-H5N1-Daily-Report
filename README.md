# 澳洲 H5N1 疫情與 Nestlé Blayney 廠地緣風險自動化報告系統

本專案為獨立之澳洲 H5N1 禽流感疫情 GIS 自動更新報告系統。透過 GitHub Actions 每天自動爬取澳洲與地方政府官網及新聞 RSS 最新數據，結合地理編碼 API 自動更新網頁 GIS 地圖，並自動部署發布於 GitHub Pages 上。

---

## 🌟 核心功能特點
1. **全澳州聯防監控網絡與多重抗封鎖中繼陣列 (curl_cffi & Playwright & Cloudflare Worker)**：同時爬取**澳洲聯邦農業部 (DAFF)** 以及**澳洲全部 8 個州/領地政府**的官方禽流感站點。導入多重抗封鎖架構：優先以 **`curl_cffi` Chrome TLS 指紋偽裝** 與 **Cloudflare Worker 代理** 繞過機房 IP/WAF 阻擋，備有 **Playwright 真實瀏覽器（啟用 `--disable-http2` 防護）** 與 **Google News RSS 兜底**，確保數據 100% 不漏報、不中斷。
2. **雙軌歷史對齊與 8/12 最新事件導向架構 (Dual-Track Event-Based Architecture)**：
   - **歷史指標 (截至 2026-08-12 17:00 AEST 官方凍結)**：完整封存保存**全澳 236 隻單鳥確診 / 55 起事件**歷史資料庫 (`cases.json`)。
   - **最新動態指標 (2026-08-12 19:00 AEST 起最新政策)**：因應 DAFF 官方改採國際標準「確診事件導向 (Positive Events)」，系統全面同步最新 **151 起確診事件 (Positive Events)** 與 **1,307 起陰性排除事件**（南澳 93 起、維州 43 起、西澳 10 起、新州 4 起、昆州 1 起），數據庫獨立為 `cases_events.json`，新舊數據雙軌 100% 完整保留不覆蓋。
3. **Gemini LLM / Vision AI 雙重情報擷取引擎**：當政府官網 HTML 因阻擋或防火牆無法直接爬取時，系統會自動使用 Playwright 專門擷取 `div#event_reporting` / `div#infographics` 數據區塊，最後呼叫 **Gemini Vision API**（搭配 `gemini-2.5-flash` / `gemini-2.0-flash` 多模型 429 重試）高對比精確辨識最新確診事件數字；並配合 **Gemini Flash LLM 文字情報提取** 解析自由文本新聞。
4. **零殘留暫存截圖生命週期管理 (Zero-Footprint Screenshot Lifecycle)**：為了防止每日自動排程截圖造成 GitHub 倉庫儲存空間膨脹（Repository Bloat），系統將截圖檔名固定為 `daff_screenshot_temp.png`，在 Gemini API 讀取完畢後**第一時間於記憶體中刪除**；並搭配 `.gitignore` 檔案雙重封鎖，確保 0 圖片殘留於 GitHub 歷史中。
5. **安全動態案例編號分配 (Safe Max-ID Calculation)**：爬蟲進行動態新地點識別時，會自動掃描歷史資料庫中最大的 CASE 編號（`max_id`）進行遞增（如 `CASE-067`），確保既有病例與最新確診完全不被重複或意外覆蓋。
6. **媒體確診交叉驗證 (C 方案)**：結合「主流媒體白名單」與「官方首長/國家實驗室發言人及確診詞」雙重過濾，自動將媒體報導的最新疫情於官方網站同步延遲期間內搶先升級，並於前端地圖與表格自動標示精緻的 **`⚠️ 媒體先行 (官網同步中)`** Badge，保證極高的時效性與數據真實性。
7. **動態最短距離計算 (Haversine 公式)**：自動計算各病例到 Nestlé Blayney 廠的球體直線距離，並在網頁頂部標籤、地緣安全宣告、最下方三大黃金論點等處自動更新最近距離。
8. **自適應動態參考文獻庫**：底部的參考資料（References）完全動態生成，會根據當前數據庫中病例所分布的省份，自動追加該省政府農業廳的官方監控網址（包含維多利亞州 Agriculture Victoria 2026-08-12 最新專區 URL）。
9. **雙時區對齊與商業家禽 100% Area Freedom 驗證**：最後編譯時間自動校正顯示台北時間與澳洲 AEST 時間，並確認全澳與紐西蘭商業家禽產業維持 0 宗感染（100% 零感染 Area Freedom 安全狀態）。

---

## 📂 檔案目錄結構
* **`cases.json`**：**歷史單鳥隻數資料庫 (歷史凍結點)**。封存截至 2026-08-12 17:00 AEST 官方凍結之 236 隻單鳥確診資料，維持完整性不被改寫。
* **`cases_events.json`**：**動態事件資料庫 (2026-08-12 起即時追蹤)**。獨立存放 2026-08-12 19:00 AEST 官方改版後之 151 起 Positive Events 最新事件節點。
* **`h5n1.py`**：自動爬取官方與新聞 RSS，結合 `curl_cffi`、Playwright 截圖與 Gemini Vision/LLM AI 情報識別、自動定位新地點、執行權威對帳與 `max_id` 安全編號分配，並編譯輸出 `index.html` 的 Python 核心引擎。
* **`report_template.html`**：網頁 GIS 報告模板（整合 Leaflet.js 地圖、Tailwind CSS 樣式、DAFF 8/12 政策改版宣告橫幅與專屬金色 🏭 Nestlé Blayney 工廠地標）。
* **`.gitignore`**：版本控制排除設定檔（徹底封鎖臨時截圖與 Python 快取檔，維護 Git 倉庫輕量化）。
* **`GOVT_SCRAPING_BEST_PRACTICES.md`**：**政府公開資料爬取與抗封鎖架構開發經驗指南**（供未來開發其他政府數據專案參考）。
* **`.github/workflows/auto_update.yml`**：GitHub Actions 定時自動化工作流設定檔（安裝 `curl_cffi` 與 Playwright，每天定時執行 2 次，自動 commit 與 push 最新 `index.html` 與 `cases_events.json`）。
* **`index.html`**：編譯後生成的正式報告網頁。
* **`live_page.html`** / **`live_page_utf8.html`**：同步生成之線上備用部署網頁。
* **`walkthrough.md`**：專案開發與 Bug 修正軌跡日誌。
* **`task.md`**：任務排程與完成度檢核表。
* **`更新說明`**：最後檔案同步日期更新於 2026-08-12 21:25（完成 DAFF 2026-08-12 19:00 AEST 最新「事件導向 (Event-based Reporting)」政策對齊，升級為全澳 **151 起確診事件 (Positive Events)** / **1,307 起陰性排除**：南澳 93 起、維州 43 起、西澳 10 起、新州 4 起、昆州 1 起。維州 Agriculture Victoria 專區網址同步更新為最新 URL。歷史數據庫 `cases.json` 100% 完整保留凍結，新版事件資料庫劃分為 `cases_events.json`。頂部 Banner、數據看板、地圖、表格、趨勢圖與文字摘要 100% 精確同步）。
