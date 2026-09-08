# AGENTS.md - 澳洲 H5N1 疫情監控與風險評估系統核心原則與知識庫

本文件為全體 AI Agent、自動化腳本與協作開發之**最高指導原則**。所有風險評估演算法、報告撰寫、簡報生成及數據解析均必須嚴格遵守以下核心概念，嚴禁偏離。

---

## 🚨 核心第一準則：NSW 商業家禽場零感染是唯一的生死防線 (Absolute Red Line)

### 1. 商業與貿易現實 (Business & Trade Reality)
* **工廠地理位置**：雀巢普瑞納工廠位於澳洲新南威爾斯州（Nestlé Purina Blayney Factory, NSW）。
* **台灣檢疫法規以「州轄區 (State Jurisdiction)」為宣告單位**：
  * 依據台灣農業部動植物防疫檢疫署 (BAPHIQ) 與國際進口檢疫規範，台灣針對高致病性禽流感 (HPAI) 的疫區認定是**以「州 (State)」為獨立管制單位**。
  * **一旦 NSW 境內「任何一處」商業家禽飼養場（無論是蛋雞場、肉雞場、種雞場）確診 H5N1，遊戲立刻結束 (Game Over)**。
  * 台灣將即刻公告新南威爾斯州 (NSW) 為禽流感疫區，雀巢 Blayney 廠之禽肉相關原料及寵物食品將被立即實施**全面進口封鎖 (Import Ban / Trade Embargo)**，台灣市場將暫時完全無法取得任何該廠產品。

### 2. 風險評估錨點之嚴格規範 (Risk Assessment Evaluation Anchor)
* ❌ **絕對禁止犯的錯誤**：
  * **嚴禁**以「疫情爆發點距離 Blayney 工廠本身的物理距離（如距離工廠幾公里）」作為評估供應鏈安全與否的主要依據。
  * 即使疫情發生在距離 Blayney 廠 300 公里外的 Hunter Valley 或 Tamworth 家禽場，只要是在 NSW 境內確診，對台灣進口而言**風險就是 100% 致命中斷**。
* ✅ **唯一正確的評估標準**：
  * 評估標準必須聚焦於 **「疫情是否逼近 NSW 州界與轄區」** 以及 **「NSW 境內野鳥疫情是否具備外溢至商業家禽飼養聚落的風險」**。
  * 評估重點維度：
    1. **NSW 全州商業家禽 0 確診狀態 (Area Freedom Status)**：這是供應鏈維持運作的最高前提。
    2. **野鳥確診逼近 NSW 轄區之動態**：包含維州 (VIC) 北進、南澳 (SA) 東移，以及新州沿海向內陸家禽走廊擴散之趨勢。
    3. **NSW 商業家禽重鎮防護力**：關注 Tamworth、Hunter Valley、Riverina、Sydney Basin 等家禽密集區之生物安全 (Biosecurity) 與圈養令措施。

---

## 🦅 候鳥與野鳥數據之正確認位 (Role of Wild Bird Data)

1. **野鳥數據是「領先指標 (Leading Indicator)」，非終點指標**：
   * eBird、Movebank 衛星航跡、GBIF 與 ALA 之野鳥觀測數據，是用於**預測病毒向 NSW 轄區擴散之時間與路徑**。
   * 候鳥大量抵達代表「暴露機會增加」，但真實風險需結合 **「野鳥帶原率」**、**「NSW 境內是否有確診事件」** 及 **「媒體報導之群聚死亡規模」** 進行交叉綜合判斷。
2. **DAFF 官方「確診事件制 (Positive Events)」之判讀原則**：
   * DAFF 官方數據採事件制（全澳 Positive Events），**單一事件可能為 1 隻死鳥，亦可能為數千隻海鳥群聚死亡**。
   * 必須透過新聞媒體 (ABC News, Guardian, PIRSA/DPIRD 公告) 提取之群聚規模 (Cluster Scale)、死亡估計隻數與哺乳類跨物種外溢 (Mammal Spillover，如紅狐) 進行嚴重度加權 (Event Severity Weighting)。

---

## 🛡️ 系統架構、資安與維運鐵律

1. **企業資安白名單 CDN 規範**：
   * 專案內所有 HTML 範本（主頁、英文主頁、風險評估模型、16:9 簡報）之 `Chart.js` 與 `Leaflet` 圖資庫，**一律使用 Cloudflare Enterprise CDN (`cdnjs.cloudflare.com`)**。
   * **嚴禁使用** `cdn.jsdelivr.net` 或 `unpkg.com`，避免引發雀巢企業資安與 Windows Defender 阻擋。
2. **零跨域阻擋前端架構 (Zero-CORS Embedded Architecture)**：
   * 所有動態數據（`bird_data.json`、`gbif_bird_data.json`、`movebank_tracks.json`、`cases_events.json`）必須同步生成對應之 `assets/js/*.js` 檔，並掛載至 `window.*Embedded`。
   * 確保同仁直接雙擊 HTML 檔案在本地端 (`file:///`) 離線開啟時，所有圖表與 GIS 航跡均可正常載入。
3. **每週雙週報自動留檔機制**：
   * 每週一固定排程產出，並另存帶有日期區間之獨立檔案至 `weekly_reports/`：
     * `weekly_reports/h5n1_weekly_report_YYYYMMDD_YYYYMMDD.html`
     * `weekly_reports/risk_assessment_weekly_YYYYMMDD_YYYYMMDD.html`
     * `weekly_reports/risk_assessment_weekly_en_YYYYMMDD_YYYYMMDD.html`
   * 任何週二至週日之手動或自動執行，皆須自動錨定前一整週週期（防呆追補機制）。

---

## 📌 開發與維護檢核清單 (Pre-Flight Checklist)

在任何程式碼修改或文字更新前，必須確認：
- [ ] 是否牢記「NSW 商業家禽場 0 確診」是台灣進口之唯一核心，沒有以「離工廠幾公里」模糊焦點？
- [ ] 是否確認風險評估著眼於「距離 NSW 轄區遠近」與「NSW 商業農場外溢可能性」？
- [ ] 是否維持全澳商業家禽、蛋場、乳牛、豬場「0 確診」之 Area Freedom 正確陳述？
- [ ] 是否確保所有 CDN 引用皆符合 Cloudflare 資安白名單？
- [ ] 是否維持中英文雙語（`index.html` / `index_en.html`、`risk_assessment.html` / `risk_assessment_en.html`、`risk_assessment_slides.html` / `risk_assessment_slides_en.html`）100% 同步？
