# 政府公開資料爬取與抗封鎖架構開發經驗指南 (Government Data Scraping Best Practices)

> **專案背景**：本指南總結自《澳洲 H5N1 禽流感與 Nestlé Purina Blayney 廠地緣風險自動監控系統》開發歷程，旨在為未來開發各國政府公開資料、農業部、衛福部或高嚴格度 WAF 保護網頁時，提供標準化的技術架構與應對策略。

---

## 🛡️ 一、 政府網站常見的資安阻擋機制與成因

政府機關網站（如 Australia DAFF, US USDA, 台灣農業部等）通常部署於高規 Cloudflare Enterprise、Akamai 或 Imperva WAF 後方，常見封鎖形態如下：

| 封鎖現象 | 成因說明 | 傳統做法失敗原因 | 最佳解法 |
| :--- | :--- | :--- | :--- |
| **機房 IP/Geo-blocking** | 政府網站預設封鎖國外 IP 或 AWS/Azure/GitHub 雲端數據中心 IP。 | 在 GitHub Actions 直接發送 HTTP 請求或 curl 會被 100% 擋下。 | 部署 Cloudflare Worker 中繼代理、或使用第三方 Web Proxy (CodeTabs, ThingProxy)。 |
| **Cloudflare-to-Cloudflare 拒絕** | 代理主機與目標網站皆在 Cloudflare 上，觸發 Cloudflare 內部防護。 | 傳送 HTTP 請求時無瀏覽器 Cookie / Header / JS Token。 | 搭配 `curl_cffi` 模擬真實 Chrome 120 TLS 指紋，或使用 Playwright 啟動無頭瀏覽器。 |
| **Link Rot / 網址改版與刪除** | 政府更新疫情時直接替換 URL 或修改 DOM 結構。 | 硬編碼 DOM Selector (`soup.find('div', class_='cases')`) 容易因改版斷裂。 | 導入 **Google News RSS 兜底防線** 與多重通用模糊內文提取。 |
| **資料不透明/不提供座標** | 政府僅宣布「某州新增 N 例」，拒絕提供海灘/城鎮精確名稱。 | 找不到地名導致無法呼叫 Geocoding API 轉換經緯度，造成數字漏算。 | 導入 **智慧對帳與盲區自動補齊機制 (Reconciliation Engine)**。 |

---

## 🏗️ 二、 核心技術模組與架構設計

為確保政府公開數據 100% 不漏報、不斷連，建議採用以下**四層防禦陣列架構**：

```
                           [使用者/自動排程 GitHub Actions]
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
         [策略 1: 多重抗封鎖中繼]                         [策略 2: 新聞 RSS 兜底防線]
   (CF Worker / curl_cffi / Playwright)                 (Google News RSS 內文提取)
                  │                                               │
                  └───────────────────────┬───────────────────────┘
                                          ▼
                             [策略 3: NLP 地理座標轉換]
                       (Local Gazetteer -> Nominatim API)
                                          │
                                          ▼
                       [策略 4: 智慧自動對帳與盲區補齊引擎]
                    (Reconciliation Engine: 確保與官方總數 100% 對齊)
                                          │
                                          ▼
                               [最終 HTML 報告與 GIS 部署]
```

### 1. 多重抗封鎖 HTTP 抓取器 (`smart_fetch_url`)
實作降級（Fall-back）鏈條：
1. **Cloudflare Worker 代理** (`CF_WORKER_URL`)：利用輕量 Edge Worker 轉發。
2. **`curl_cffi` 指紋偽裝**：模擬真實 Chrome TLS/JA3 指紋發送連線。
3. **Playwright 真實瀏覽器**：執行無頭 Chromium 模擬真人瀏覽與渲染 JavaScript。
4. **第三方跨域 Web Proxy 陣列**：輪詢 `api.codetabs.com` / `thingproxy.freeboard.io` / `api.allorigins.win` / `corsproxy.io`。
5. **標準 requests 兜底**。

### 2. 新聞 RSS 兜底與媒體先行驗證 (News RSS Fallback)
- **新聞 RSS 兜底**：當政府官網遭極強 WAF 封鎖時，Google News RSS 會定期快取新聞摘要。透過模糊正則匹配提取新疫情關鍵字。
- **媒體先行驗證 (C 方案)**：結合「權威媒體白名單（如 ABC News, BBC）」與「官方首長發言人詞（如 Minister, CSIRO, ACDP）」，在官網尚未更新的空檔期搶先登錄案例，並標註 `⚠️ 媒體先行 (官網同步中)`。

### 3. 地理座標 API 降級策略 (Geocoding Fallback Chain)
- **Local Gazetteer（離線地名快取庫）**：優先比對常見重要城鎮，0 延遲且免去 API 限流風險。
- **Nominatim API (OpenStreetMap Rate Limit 防護)**：嚴格符合 OpenStreetMap Usage Policy 規範，每次 API 請求間加入 `time.sleep(1.0)` 延遲，防止多個新地點併發請求時觸發 HTTP 429 Rate Limit。
- **多段退避**：自動剔除 "Beach", "Jetty", "Coast" 等邊緣字尾，提高匹配率。
- **Geocoding Proxy**：將 Nominatim 請求同樣透過 Cloudflare Worker 轉接，避免 GitHub Actions 共享 IP 被 OpenStreetMap 封鎖。

### 4. 智慧自動對帳與盲區補齊機制 (Reconciliation Engine)
- **原理**：強制提取政府發布的控制目標總數 `target_totals`（如 `{"SA": 42, "VIC": 7}`）。
- **對帳比對**：計算目前地圖上已標示之精確座標案例總數 `current_counts`。
- **盲區補齊**：當 `target > current` 時，自動生成 `【官方已確診，未公布具體地點】` 的虛擬盲區個案（錨定於該州沿海概略座標），保證前端儀表板、圖表與地圖總數 **100% 永遠對齊官方真實公告**！

---

## 📜 三、 專案歷史版本演進說明 (Development Changelog)

| 版本 | 發布日期 | 核心改動內容 | 解決之痛點 |
| :--- | :--- | :--- | :--- |
| **V1.0** | 2026-07-04 | 初始化單頁 HTML 報告與靜態病例數據。 | 建立雛形報告。 |
| **V2.0** | 2026-07-27 | 導入 TailwindCSS、Leaflet.js GIS、Chart.js 與 GitHub Actions 自動排程。 | 實現視覺化與每日自動更新。 |
| **V3.0** | 2026-08-01 | 升級全澳 8 州聯防爬蟲、Cloudflare Geocoding 代理、鳥類密度動態圈圈與雷達水波。 | 對應 8/1 全澳大暴增 20 例，解決 IP 封鎖與視覺密度呈現。 |
| **V4.0** | 2026-08-03 | 導入 **智慧對帳與盲區補齊引擎 (Reconciliation Engine)**、多重 Web Proxy 陣列、動態日期與情境摘要生成。 | 解決 62 例官方對帳落差、官網未釋出具體地名問題、與極強 WAF 阻擋。 |
| **V5.0** | 2026-08-11 | 導入 `curl_cffi` TLS 指紋偽裝、Playwright `--disable-http2` 防護、Gemini Vision 多模型與 429 Rate Limit 重試降級，以及零殘留暫存截圖清理機制 (`.gitignore` + in-memory remove)。 | 解決 Akamai/Cloudflare `ERR_HTTP2_PROTOCOL_ERROR` 封鎖、Gemini API 429 超限與 Git 倉庫圖片膨脹痛點。 |

---

> **開發經驗總結**：未來在開發任何政府數據抓取專案時，**「絕對不要只依賴單一 URL 或單一解析邏輯」**。必須結合「多重 HTTP 通道 + 新聞 RSS 兜底 + 智慧對帳補齊」，才能確保系統在政府改版、阻擋或隱匿數據時，依然穩如泰山。
