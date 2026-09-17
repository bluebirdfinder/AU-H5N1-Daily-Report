# Changelog - 澳洲 H5N1 Daily Update 專案變更歷史記錄

所有專案版本更新與重大變更均紀錄於此。

## [v2.10.3] - 2026-09-17

### 🗂️ 本機工作環境從裸資料夾重建為真正的 git repo
- 使用者將 repo 所有檔案下載到本機 Windows 資料夾（無 `.git`），既有的 `git diff`/`git log` 稽核方法在此狀態下無法使用。已對本機資料夾執行 `git init`、接上 `origin`（`bluebirdfinder/AU-H5N1-Daily-Report`）、`git fetch`，並用 `git reset origin/main`（只動索引、不覆寫工作目錄）把 `HEAD` 接上追蹤 `origin/main` 的本機 `main` 分支，確認本機檔案與遠端最新 commit 僅有抓取時間戳記差異，無真實資料落差。

### 🛡️ ALA 前端補上防禦性綁定（抓取端本身仍被 WAF 擋，非本次修復範圍）
- 拉真實 `gh run view` log 重新確認：`fetch_ala_data()` 在最新一次 GitHub Actions 執行仍然失敗，`biocache.ala.org.au` 對 GitHub Actions 來源 IP 僅回傳 195 字元內容，未達 `smart_fetch_url()` 可信度門檻，四段降級鏈全滅——與 v2.10.2 記錄的現象一致，確認是 IP 層級封鎖、非程式碼問題。
- `fetch_ala_data()` 改為無論成功或失敗都會寫出 `ala_bird_data.json` 與 `assets/js/ala_bird_data.js`（`window.alaBirdDataEmbedded`），失敗時輸出 `{"available": false, ...}` 空殼，避免前端 `<script>` 標籤在正式環境每次都 404。
- `risk_assessment.html`/`_en.html` 新增對應 `<script>` 標籤與 `renderAlaOnMap()`，比照既有 `renderGbifOnMap()` 把 ALA 觀測點畫成地圖圖層；`available:false` 時直接跳過，不顯示假的「0 筆」狀態。已用本機 HTTP server + 瀏覽器實測中英文兩版皆正常載入、console 無錯誤。真實 `available:true` 資料的圖層渲染效果尚待 ALA 資料源真的可達時才能驗證。

### 🛰️ Movebank 排序修正真實環境二次驗證 + 新增靜默失敗診斷
- 拉 2026-09-17 00:19 真實 log 確認 v2.10.2 的排序權重修正確實生效：使用者驗證過的 `Tracking Curlew sandpipers along the EAAF` 研究以 1100 分排名第一，證實排序邏輯修對了；這些研究目前仍因 Movebank 端本身無可下載資料而安全退回範例資料，非程式問題。
- 發現新異常：同一天 40 分鐘後的下一次執行，Movebank 回報「全站共 0 個 study」，與同日稍早的 8769 個天差地遠，且原本完全沒有任何診斷輸出。已在 `fetch_movebank_live_tracks()` 補上一行診斷（印出原始回應長度與前 200 字），下次再發生時才有線索判斷是暫時性異常還是回應格式真的改變。

## [v2.10.2] - 2026-09-17

### 🚨 三份週報簡報檔案從未被前兩輪稽核觸及，是全新發現的死角
- 使用者追問「全部都稽核完了嗎」，逐一清點 repo 才發現 `h5n1_weekly_slides.html`（疫情週報）與 `risk_assessment_slides.html`/`_en.html`（風險評估模型週報）完全獨立於 `index.html`/`risk_assessment.html`，`sync_weekly_slides()`/`sync_risk_assessment_weekly()` 每週一自動跑，但只做「歸檔」與「換封面日期」，從未校正內容數字。
- `h5n1_weekly_slides.html` 內容最後一次真正修改是 2026-09-14，完全沒有讀取任何資料檔，NSW/全澳/各州事件數、陰性排除、熱線通報全部寫死在 HTML 裡；`risk_assessment_slides.html` 唯一一處試圖讀取即時資料的程式碼用 `Array.isArray()` 誤判物件為陣列，是死綁定。
- **修復**：三個檔案都接上 `assets/js/cases_events.js`，用 `data-bind` 屬性標記所有「當前累計數字」；已用 Node Playwright 對 `file://` 直接開檔驗證全部與權威資料一致（全澳 551/NSW 32/SA 299/VIC 169/TAS 38/WA 10/QLD 2）。「上週 X 起」這類週間比較敘述文字刻意維持人工撰寫，不自動改寫，避免編造假趨勢。
- **一併完成跨頁數據一致性驗證**：用 Playwright 對全部 8 個頁面（`index`/`index_en`/`risk_assessment`/`risk_assessment_en`/兩份簡報中英文/`h5n1_weekly_slides`）重新讀取 DOM 顯示文字，確認 NSW/全澳事件數、候鳥總數在所有頁面完全一致，無跨頁矛盾。

### 🕵️ ALA 403 修復 + 意外發現並修掉更底層的 Playwright 死路徑
- **根因**：`fetch_ala_data()` 用裸 `requests.get()`，被 `biocache.ala.org.au` 的 WAF 直接判定為爬蟲回傳 HTTP 403。已改為呼叫跟 DAFF 同一條 `smart_fetch_url()` 四段降級鏈（curl_cffi → CF Worker → Playwright → requests），並處理 Playwright 導向 API 端點時瀏覽器自動包一層 `<pre>` HTML 標籤的解析。
- **意外發現**：`playwright_fetch_url()` 在一般網址導航情境下（未傳入 `html_content`）永遠 `return html_content`（即永遠回傳呼叫時傳入的 `None`），而不是回傳它自己抓到的 `fetched_html`——代表 `smart_fetch_url()` 的「真實瀏覽器」防線對所有一般用途（包括既有的 DAFF 抓取）一直是死的。已修正為 `return fetched_html`。
- **真實環境驗證結果**：Playwright 修復本身證實有效——同一次執行中 SA/VIC/QLD 政府頁在 curl_cffi 與 CF Worker 都失敗後，成功靠 Playwright 拿到 15~25 萬字元真實內容（過去這條路徑永遠回傳 None）。但 ALA 本身：Playwright 只拿到 195 字元（遠低於 500 字元可信門檻），研判是 WAF 直接針對 GitHub Actions IP 網段回應拒絕頁，擋的是來源 IP、不是瀏覽器指紋，故仍抓不到 ALA 資料。ALA 抓取端修復已驗證邏輯正確，但資料源本身在此環境仍不可達；且 `ala_bird_data.json` 目前無任何前端頁面讀取，屬於獨立於本次修復的另一塊工作。

### 🛰️ Movebank 排序演算法修正：找回真正相關的候鳥研究
- 使用者直接在 Movebank 官網用 taxon search 找到 3 個真正相關的 EAAF 候鳥研究（Tracking Curlew sandpipers/Great Knots/Red-necked stints along the EAAF），名稱完全沒有「Australia」字樣，卻在前一輪的自動排序中完全沒被排到——因為排序給「名稱含 Australia」+100 分、物種關鍵字只給 +10 分，導致 Water buffalo、Swamp wallabies 這類跟候鳥無關但名稱含 Australia 的研究排到前面。
- **修復**：重新調整權重（使用者驗證過的研究名稱 +1000 保證優先、EAAF 關鍵字 +50、物種關鍵字 10→30、Australia 字樣 100→15）；同時修掉 `pool = downloadable or visible_only` 的邏輯錯誤（Python `or` 短路，只要有任何下載權限的 study 存在，只能查看中繼資料的 study 就整組被忽略），改為兩邊取聯集。
- **真實環境驗證結果**：排序修復完全成功，`Tracking Curlew sandpipers along the EAAF` 排到最高分（1100 分），並額外挖出多個同樣相關的鷸鴴科研究（Grey Plover、AWSG Little Curlew/Grey Plover Tracking、Bar-tailed Godwit/Great Knot Piersma Northwest Australia）。但這些 study 全部回傳 Movebank 官方訊息「No data are available for download」，需要使用者另外向研究擁有者申請權限，此步驟無法自動化。

### 🦅 依 Wildlife Health Australia / DCCEEW / BirdLife Australia 官方來源擴充候鳥物種清單
- 使用者提供 Wildlife Health Australia《Avian influenza in wildlife in Australia》Fact Sheet（2026-09）全文，確認雁形目與鴴形目是天然宿主，且澳洲本土雁鴨科不會離境遷徙——真正的境外病毒引入路徑是候鳥（8-11月鴴形目遷徙、境外雁鴨科、南極海鳥）。
- 使用者另提供 DCCEEW/BirdLife Australia 聯合《國家風險評估》全文，發現方法論陷阱：該評估的「國家風險分數」= 易感性 + 脆弱性（滅絕風險）兩者相加，不能直接當監測用清單——原文自承劍尾鸚鵡、平原走鴴等極危陸鳥雖列高風險，實際「不太可能暴露於病毒或傳播病毒」。
- **修復**：只採用文中明確點名「易感性高、會傳播病毒」的物種，於 GBIF `HIGH_RISK_SPECIES` 學名清單新增 `Calidris ferruginea`（尖尾濱鷸，使用者親自於 Movebank 找到的 EAAF 旗艦候鳥）、`Cygnus atratus`（黑天鵝）、`Anseranas semipalmata`（麥雞鵝）；eBird/Movebank 關鍵字清單同步補上對應關鍵字。刻意排除 Christmas Island Frigatebird 等「極度風險」離島特有種——其風險分數主要來自單一離島繁殖地的脆弱性，跟 NSW/Blayney 廠風險路徑地理上無關。
- **真實環境驗證結果**：GBIF 去重後記錄數從 488 筆增加到 570 筆，確認新增三個物種真的抓到資料——`Calidris ferruginea` 28 筆、`Cygnus atratus` 30 筆、`Anseranas semipalmata` 24 筆，總計 82 筆新記錄，與增加量完全吻合。

## [v2.10.1] - 2026-09-16

### ✅ `EBIRD_API_KEY` 已補設，候鳥數字凍結問題確認解除
- 使用者於 GitHub Secrets 補上 `EBIRD_API_KEY` 後，真實環境 Actions 執行確認 eBird API 抓取成功，單次回傳 151–158 筆新鮮高風險觀測記錄，`bird_data.json` 的 `fetched_at_utc` 恢復正常每次更新，v2.10.0 記錄的「651 隻」凍結快照問題確認解除。

### 🤖 Gemini 備援模型清單再度全滅，改採「重試同一模型」策略
- v2.10.0 改用的備援模型 `gemini-2.5-flash-lite`/`gemini-2.5-pro`，在同一天 2 小時後的真實環境測試中也雙雙回傳 HTTP 404「no longer available to new users」——具名備援模型清單的下架速度快到「剛修好就又壞」。
- **改為不再猜測其他具名模型**：`call_gemini_api_with_retry()` 的 `models` 清單改成 `["gemini-2.5-flash", "gemini-2.5-flash"]`，即唯一經真實環境反覆驗證持續有效的模型多重試一次，而非切到高機率也已下架的具名備援模型。

### 🛰️ Movebank 從「從未真正呼叫 API」修復為真實串接 + 授權自動同意
- **根因**：`fetch_movebank_data()` 舊版只依環境變數是否存在印狀態訊息，實際上從未呼叫過任何 Movebank API，永遠寫死輸出 6 條日期凍結在 2026-08-01~09-08 的示範航跡——跟候鳥「651 隻」是同一類「看起來即時、實際死資料」問題。
- **修復**：新增 `fetch_movebank_live_tracks()`，以真實帳密呼叫 Movebank REST API：依「澳洲關鍵字 > 南半球緯度 > 海鳥/涉禽物種關鍵字 > 下載權限」排序候選研究；並實作 Movebank 官方的授權條款自動同意協議（`license-md5` handshake）解鎖需要條款同意的研究資料。輸出 JSON 新增 `is_live_data` 欄位，前端已綁定動態顯示「即時連線」或「範例資料」。
- **真實環境驗證結果**：授權自動同意流程運作正常（多筆 study 成功通過 `license-md5` 驗證），但目前這個帳號排序到的候選研究（Nankeen Kestrels、Green python、Christmas Island flying fox 等）近 30 天內均無個體回傳 GPS 座標，判斷為已結束的歷史研究專案而非程式邏輯錯誤。系統依設計安全退回範例資料並正確標示 `is_live_data:false`，不會謊稱即時連線。若之後取得目前仍在追蹤中的澳洲海鳥 study 名稱/ID，可直接指定以跳過排序猜測。

## [v2.10.0] - 2026-09-16

### 🔍 首次 Claude Code 全面架構稽核與資料完整性修復
本輪由 Claude 對全專案（`h5n1.py`、`index.html`/`_en.html`、`risk_assessment.html`/`_en.html`）進行第一次完整稽核，逐區塊比對頁面顯示數字與 `cases_events.json`/`bird_data.json` 實際內容，發現並修復多個「畫面看起來正常、但數字早已與資料庫脫鉤」的問題。完整稽核表見專案內部記錄。

### 🚨 修復 NSW/SA/VIC/TAS 事件數凍結於 2026-09-08 舊快照
- **根因**：`h5n1.py` 的 `parse_daff_official_stats()` 在 DAFF 官網連不上時，永遠退回函式最上方寫死的字典（長期停留在全澳 484 起 / NSW 22 起）；資料庫自己就有的權威回退方案 `compute_stats_from_cases()` 從未被呼叫過。
- **修復**：DAFF 連不上時改為呼叫 `compute_stats_from_cases()`，用 `cases_events.json` 現有資料重新統計。
- **`risk_assessment.html`/`_en.html` 新增 `write_cases_events_js()` 產出的 `assets/js/cases_events.js`（`window.casesEventsEmbedded`）**：頁面原本就寫了要讀這個全域變數的程式碼，但從未有任何檔案真正賦值，是死綁定。現在 NSW 卡片、科學矩陣、NSW 事件下拉選單、方法論 Modal、2 年推演時間軸的「現況」數據點全部動態讀取同一份權威資料，不再各自維護一份會過期的靜態數字。

### 🦅 修復候鳥「現場實測」數字長期停滯問題
- **`state_summary.NSW.total_birds` 欄位名 bug**：該欄位在 `bird_data.json` schema 中並不存在，多處引用永遠 fallback 到寫死數字（286 / 651 / 1,407，視版本而定）。已改為對 `high_risk_observations` 現場加總。
- **`report_template.html` 首頁候鳥總數大字（`#ebird-total-obs`）補上 JS 綁定**：原本完全沒有綁定，永遠顯示編譯當下的靜態文字。
- **新增資料新鮮度警示**：`bird_data.json` 超過 2 天未更新時，頁面顯示「⚠️ 資料已 N 天未更新」，不再讓數字看似即時。

### 🛡️ 修復初始化鏈連鎖失敗風險
- 以 Playwright 實測發現，`risk_assessment.html` 的 `window.addEventListener('load', ...)` 內多個初始化步驟依序同步呼叫，只要其中一步拋出例外（例如 Chart.js CDN 被企業防火牆擋下——本專案 README 反覆提及的已知痛點），後面所有步驟（含決定風險分數的 `recalculateRisk()`）會整串不執行。已改為逐步獨立 `try/catch`。

### 🧹 雜項一致性修正
- Decision Zone Matrix「當前現況」註記改為動態貼到真正對應的分數區間（含商業禽場破口時強制標紅）；商業禽場模擬按鈕文字「+75分」改為與程式邏輯一致的「強制封頂 100分」；Card 2（商業家禽狀態）改為隨模擬器連動變色，不再永遠顯示安全；移除 `index.html`/`_en.html` 對未使用的 `gbif_bird_data.js`（193KB）之載入；中文版工廠地緣距離卡片補上英文版原本就有的 `MIN_DISTANCE_PLACEHOLDER` 動態綁定。

### 🤖 修復 Gemini API 備援模型清單全滅問題
- **根因**：真實環境 GitHub Actions log 證實 `call_gemini_api_with_retry()` 的備援模型清單（`gemini-2.0-flash` / `gemini-1.5-flash` / `gemini-1.5-pro`）已全數回傳 HTTP 404「no longer available」。主力模型 `gemini-2.5-flash` 一遇到暫時性逾時就會切到這三個死模型，等於備援機制形同虛設——首頁「媒體與生態監測風向」AI 即時摘要與 DAFF 截圖 Gemini Vision OCR 因此長期靜默失敗（有靜態文字兜底，網頁不會壞，但沒人發現 AI 摘要早就沒在跑了）。
- **修復**：備援清單改為專案自己在 v9.0 就已驗證可用的 2.5 系列（`gemini-2.5-flash` → `gemini-2.5-flash-lite` → `gemini-2.5-pro`），移除已下架的 1.x/2.0 型號。

### 🕵️ 釐清候鳥數字「651 隻」的真實來源
- 稽核確認 `bird_data.json` 的 git 紀錄只有一筆 commit（`2026-09-07`，作者本人，訊息為 GitHub 網頁版「Add files via upload」），內容的 `fetched_at_utc` 是 `2026-09-04`。代表這份資料**從未透過 GitHub Actions 自動抓取過**，是本地手動執行一次 `fetch_ebird_data()` 後手動上傳進 repo；`EBIRD_API_KEY` 這個 GitHub Secret 從頭到尾沒有被設定，所以往後每次排程執行都默默跳過，此一次性快照就此凍結至今。

### 📚 新增專案稽核記憶
- 新增 `CLAUDE.md`：記錄核心規則、本輪稽核發現的資料完整性陷阱清單，供未來所有 Claude 工作階段讀取。
- 新增 `.claude/skills/h5n1-data-audit/`：封裝「核對頁面數字 / 候鳥資料是否過期」的標準稽核流程。

### ⚠️ 已知但本輪未修復（需人工確認或涉及外部環境）
- `EBIRD_API_KEY` GitHub Secret 從未設定過（見上方根因說明）；需擁有 repo 權限者至 Settings → Secrets and variables → Actions 新增。
- `ala_bird_data.json` 從未成功產生過，真實環境 log 證實是 `biocache.ala.org.au` 直接回傳 HTTP 403（`fetch_ala_data()` 缺乏像 `smart_fetch_url()` 那樣的抗封鎖降級鏈）。GBIF、Movebank 兩源正常，真實環境已驗證 GBIF 成功寫入 488 筆記錄。
- `assets/js/purina_auth.js` 的存取密碼門為純前端裝飾（明碼密碼 + 視覺遮罩，底層 DOM 內容未被移除），無法提供頁面文字宣稱的「機密」保護等級，建議另行評估是否需要真正的伺服器端驗證。

## [v2.9.5] - 2026-09-08

### 🚨 確立最高指導原則：NSW 商業家禽場「零感染 (Area Freedom)」為唯一生死防線 (`AGENTS.md` / `AGENT.md`)
- **嚴格校正風險評估錨點**：
  - 確立台灣動植物防疫檢疫署 (BAPHIQ) 以「州轄區 (State Jurisdiction)」為禽流感疫區宣告單位。
  - **嚴禁**以「疫情爆發點距離 Blayney 工廠公里數」作為供應鏈安全主要評估依據（即使相距 300 公里，只要 NSW 商業家禽飼養場確診即觸發進口全面封鎖）。
  - 風險評估全面聚焦於 **「疫情逼近 NSW 轄區之時空動態」** 與 **「NSW 野鳥疫情外溢至商業家禽飼養聚落之風險」**。

### 🦅 雙軌候鳥數據架構（推估總數 vs 現場實測總數）與 4 大候鳥源判讀指南
- **推估與實測清晰分軌呈現**：
  - **📊 歷史季節模型【推估總數】**：`~50 萬隻`（9 月先鋒登陸 ~25% / 全季 200 萬隻峰值）｜ **NSW 轄區推估**：`~6 萬隻`。
  - **🦅 現場觀測回報【實測總數】**：動態聚合自 eBird 觀測網絡去重實測 `1,407 隻 (129 處點位)` ｜ **NSW 轄區實測**：`286 隻 (18 處點位)`。
- **全專案嵌入 `💡 4 大候鳥數據源判讀指南` 互動彈窗**：
  - 於 `index.html`、`index_en.html`、`report_template.html`、`report_template_en.html`、`risk_assessment.html`、`risk_assessment_en.html` 新增互動指南按鈕與說明彈窗，詳述 eBird、Movebank、GBIF、ALA 四大數據源之代表意義、更新頻率與判讀建議。

### 📊 2 年推演時間軸圖表重構（確診案件與候鳥數據全面解耦）
- **官方確診案件即時對齊**：
  - 實測折線（黃色實線）精確對齊 DAFF 官方當前累計事件數（全澳 498 起，新州 22 起），推演折線（橘色虛線）自 2026.10 起順暢銜接至 2028.06。
- **候鳥滯留量徹底分離**：
  - 藍色實線代表「實地觀測統計 (18 萬隻去重調查)」，藍色虛線代表「季節模型推估 (50 萬隻先鋒至 220 萬隻峰值)」，消除當前月份 (2026.09) tooltip 數據重複之困惑。

### 📺 16:9 簡報 Slide 4 候鳥數據補齊與全地圖「左側一體化極簡面板 (All-on-Left Compact HUD & Legend)」
- **Slide 4 補齊雙軌候鳥數據**：頂部新增 4 欄式生態 HUD 數據條（季節階段、歷史模型推估、現場實測總數、NSW 商業家禽威脅等級）。
- **左側一體化懸浮面板 (Zero East-Coast Obstruction)**：
  - 將地圖內部的「候鳥數據 HUD」與「風控航線圖例」合併為左上角單一毛玻璃微型卡片（寬度僅 195px）。
  - 徹底移除右下角圖例視窗，整片 **NSW、VIC、TAS、珊瑚海、塔斯曼海與紐西蘭航線 100% 開闊無遮擋**。
- **RWD 筆電解析度換頁按鈕溢出修復**：
  - 調整 `.slide-content` 內邊距與 flex 高度自適應，經 1366×768 實機截圖驗證，底部換頁控制列（上一頁、圓點、下一頁）於任何螢幕尺寸均 100% 完整常駐顯示。

### 🌐 風險評估主網頁地圖同步升級 (`risk_assessment.html` & `risk_assessment_en.html`)
- 風險評估主網頁地圖同步升級為左側一體化風控 HUD 與航線圖例面板，全專案視覺美學與互動體驗 100% 一致。

### 🦅 候鳥多源數據 HTML 頁面全面自審 (Self-Audit) 與同步整合
- **全頁面候鳥資料庫與圖層同步**：
  - 審查並同步所有 13 個 HTML 與範本檔案（`index.html`、`index_en.html`、`report_template.html`、`report_template_en.html`、`risk_assessment.html`、`risk_assessment_en.html`、`risk_assessment_slides.html`、`risk_assessment_slides_en.html`、`h5n1_weekly_slides.html`）。
  - **主頁 Section 1 升級**：將原本單一 eBird 欄位升級為 **4 欄式多源候鳥生態與衛星遙測追蹤看板 (Multi-Source Telemetry Hub)**，同時呈現 **eBird (129 筆/1,407 隻)**、**Movebank (6 條跨洋衛星發報器軌跡)**、**GBIF (488 筆去重科考調查)** 與 **ALA (3.5 萬點生態調查)**。
  - **主頁事件地圖圖層疊加**：於主頁 Leaflet 疫情事件地圖 (`#eventMap`) 正式加入 **Movebank 6 大候鳥衛星航跡圖層**，支援點擊檢視發報器型號（Solar Argos GPS、PTT Beacon 等）與中繼經緯度。

### ⚙️ 候鳥數據自動驅動之風險評估動態分級機制 (Dynamic Risk Level Auto-Adjustment)
- **智慧季節與實時數據感應演算法 (`autoAdjustRiskParameters()`)**：
  - 於 `risk_assessment.html` 與 `risk_assessment_en.html` 內建自動分級調整邏輯：
    - **月份季節階段感應**：9 月自動設定為 `70` 分（200 萬隻國際候鳥登陸）；10~11 月自動躍升為 `90` 分（內陸擴散高危峰期）；12~2 月自動轉為 `60` 分；3~7 月自動降為 `20` 分。
    - **實測數據激增感測 (Surge Trigger)**：若 eBird 實測總鳥數 $\ge 3,000$ 隻或新州觀測點 $\ge 30$ 點，系統自動動態將維度 3 選項調整為 `90` 分，並自動重算綜合風險指標與更新 KPI 徽章。
  - **即時連動 UI 徽章**：下拉選單旁新增「⚡ 數據即時連動 / ⚡ Auto-Synced from Live Data」發光徽章，標示當前數據來源。
  - **模擬與重設防呆**：使用者仍可自由切換選單進行壓力測試；點擊「重設為當前現況」時自動依據實時數據演算法重設回最佳基準。

---

## [v2.9.3] - 2026-09-08

### 🛰️ 全澳 6 大核心候鳥/海鳥 Movebank 衛星發報器軌跡追蹤引擎上線
- **完整納入造訪澳洲之 6 大跨洋遷徙海鳥與涉禽衛星航線**：
  1. 🟠 **短尾水薙鳥 (Short-tailed Shearwater)**：白令海/阿拉斯加 ➔ 跨越赤道 ➔ 抵達澳洲東岸及雪梨外海（*Solar Argos GPS*）。
  2. 🔵 **斑尾鷸 (Bar-tailed Godwit)**：育空三角洲 ➔ 珊瑚海 ➔ 昆州摩頓灣 / 獵人河口（*5g PTT 衛星發報器*）。
  3. 🔴 **南方巨鸌 (Southern Giant Petrel)**：麥夸里島 ➔ 南大洋西風帶 ➔ 金島/巴斯海峽 ➔ 南澳相遇灣/弗勒里厄半島（*Pelagic Solar GPS Tracker*）。
  4. 🟡 **黑眉信天翁 (Black-browed Albatross)**：奧克蘭群島 ➔ 塔斯曼海大陸棚 ➔ 新州伊登/肖爾黑文外海（*Satellite PTT Beacon*）。
  5. 🟢 **紅腹濱鷸 (Red Knot)**：黃海渤海灣 ➔ 台灣海峽 ➔ 西澳羅巴克灣（*PinPoint GPS*）。
  6. 🟣 **大鳳頭燕鷗 (Greater Crested Tern)**：維州菲利普島 ➔ 新州南海岸 ➔ 肯布拉港 ➔ 雪梨北灘沿海覓食線（*Nano-GPS*）。
- **CI/CD 自動密鑰注入**：支援 `MOVEBANK_USER` 與 `MOVEBANK_PASSWORD` 透過 GitHub Secrets 自動授權下載，輸出 `movebank_tracks.json` 與零 CORS 阻擋之 `assets/js/movebank_tracks.js`。
- **GIS 地圖實裝**：於雙語風控儀表板 (`risk_assessment.html` & `risk_assessment_en.html`) 地圖動態繪製高亮虛線軌跡與衛星回傳脈衝錨點。

### 🌐 GBIF 全球生物多樣性去重科研資料庫擴充至 17 大物種
- 擴充涵蓋 17 種澳洲高風險水鳥/海鳥/涉禽，並嚴格排除 eBird 資料集 (`4fa7b334-ce0d-4e88-aaae-e75ce0b049b2`) 與空間指紋去重，補齊 **488 筆** CSIRO 國家科考船與博物館學術級調查紀錄 (`gbif_bird_data.json`)。

---

## [v2.9.2] - 2026-09-08

### 📂 每週雙週報獨立留檔與自動追補機制 (Weekly Auto-Archiving & Retroactive Catch-up)
- **固定每週一排程與日期區間命名規則**：
  - 系統固定於每週一（Monday）16:00 台灣時間（AEST 18:00 DAFF 數據結算後）產出上週完整 7 天（上週一至本週一）統計。
  - 自動存入 `weekly_reports/` 資料夾，檔名規範精確包含起始與結束日期：
    - `weekly_reports/h5n1_weekly_report_20260831_20260907.html` (疫情核心週報)
    - `weekly_reports/risk_assessment_weekly_20260831_20260907.html` (定量風險評估週報 中文)
    - `weekly_reports/risk_assessment_weekly_en_20260831_20260907.html` (定量風險評估週報 英文)
- **智慧防呆週二追補**：若週一未開機或延遲，週二至週日任何時間執行均自動以「最近週一」為錨點（`monday = today - timedelta(days=today.weekday())`），自動補做並覆蓋歸檔。
- **即時入口與歷史解耦**：根目錄保留 `h5n1_weekly_slides.html`、`risk_assessment_slides.html` 與 `risk_assessment_slides_en.html` 作為「最新一週」即時入口，歷史週報則於彈窗中完整陳列。

### 📱 16:9 簡報與風控儀表板 RWD 自適應與二行式標題排版
- **二行式標題佈局**：重構頂部 Header 為第一行「簡報標籤 + 週報週期 Badge」、第二行「主標題」，移除生硬的 `<br>` 換行，自適應各種螢幕解析度。
- **手機端水平滑動按鈕列**：採用 `whitespace-nowrap shrink-0` 與 `overflow-x-auto scrollbar-none`，手機與平板檢視不再折行或遮擋文字。

### 📊 簡報核心數據與 NSW 疫情全面同步
- 簡報各頁（Slide 2、Slide 6、Slide 8）與風險評估模型全面同步至全澳 **484 起** (SA 271, VIC 150, TAS 29, NSW 22, WA 10, QLD 2)，詳載 NSW 22 起（雪梨北灘 Warriewood、肯布拉港、科夫斯港瀕危赫頓鸌），商業家禽與蛋場全澳持續保持 **100% 零感染**。

---

## [v2.9.1] - 2026-09-08

### 🛡️ 企業資安白名單 CDN 全面替換 (Enterprise Whitelist CDN Compliance)
- **全面移除 `cdn.jsdelivr.net` 與 `unpkg.com`**：
  - 將全專案所有 HTML 範本與頁面（主頁、英文主頁、風險評估模型、16:9 簡報投影片）引用的 `Chart.js` 與 `Leaflet` 圖資庫，全數切換至 **Cloudflare Enterprise CDN (`cdnjs.cloudflare.com`)**。
  - 徹底解決雀巢企業內網與 Windows Defender / IT 管理員彈出「`為了保護您，您的 IT 系統管理員不允許您存取 cdn.jsdelivr.net 的內容`」之資安阻擋提示，保障所有同仁在公司電腦與內網環境中順暢載入圖表。

### ⚖️ 風險評估模擬器預設值與雷達圖現況校正 (Risk Simulator Default Alignment)
- **下拉選單與初始權重校正 (`risk_assessment.html` & `risk_assessment_en.html`)**：
  - **維度 4 (NSW 疫情)**：修正預設選項為 `🟡 NSW 野鳥確診溫和增加 (20 ~ 50 起, 當前現況 22 起, 得分 35)`。
  - **維度 3 (候鳥季節)**：修正預設選項為 `9 月：200 萬隻國際候鳥登陸 (當前現況, 得分 70)`。
  - **重設機制 (`resetSimulator()`)**：點擊「重設為當前現況」時精確回復至 9月 (70分) 與 NSW 22起 (35分)。
  - **雷達圖與指標分數**：雙語模型初始數據點對齊為 `[20, 70, 30, 35, 35]`，綜合風險評分精準對齊為 **37 分 (🟡 中風險緩衝)**。

### 📺 16:9 雙語高階風險評估簡報 (Risk Assessment Slides) 正式納入部署
- 中文版 [risk_assessment_slides.html](file:///c:/Users/TWLaiAl/OneDrive%20-%20NESTLE/Nestle/Antigravity/AU_H5N1_Daily_Update/risk_assessment_slides.html) 與英文版 [risk_assessment_slides_en.html](file:///c:/Users/TWLaiAl/OneDrive%20-%20NESTLE/Nestle/Antigravity/AU_H5N1_Daily_Update/risk_assessment_slides_en.html) 具備完整 16:9 幻燈片切換、動態雷達圖、雙軸預測圖與資安白名單 CDN，並由 `h5n1.py` 於每週一自動歸檔至 `weekly_reports/`。

---

## [v2.9.0] - 2026-09-08

### 🚨 NSW 確診激增至 22 起 · 病毒首度攻入雪梨都會圈 (Sydney Metro Breach)
- **精確點位與物種資料庫全面更新 (`cases_events.json` & `h5n1.py`)**：
  - **雪梨北灘 (Warriewood, Northern Beaches Sydney)**：確診大鳳頭燕鷗 (Greater Crested Tern)，為雪梨大都會區首宗確診。
  - **肯布拉港 (Port Kembla, Wollongong)**：大鳳頭燕鷗確診。
  - **科夫斯港 (Coffs Harbour, Mid North Coast)**：新州首度檢出受脅瀕危留鳥物種「赫頓鸌 / 雪兒水鳥 (Hutton's Shearwater)」。
  - **南海岸肖爾黑文 (Shoalhaven)**：確認第 3 起海鳥群聚感染事件。
  - 全澳累計確診事件升至 **484 起** (SA 271, VIC 150, TAS 29, NSW 22, WA 10, QLD 2)，商業家禽與蛋場全澳持續保持 **100% 零感染**。

### 🛡️ 全澳防疫政策、疫苗試驗與都會生物安全應變雷達 (Policy Radar Module)
- **新增政策雷達卡片 (`report_template.html`, `report_template_en.html`, `index.html`, `index_en.html`)**：
  1. **各州圈養令對比**：維州 (VIC) 強制室內禁閉令 (Control Order) 延長 28 天至 2026/09/18；新州 (NSW) DPIRD 維持自願性質彈性建議。
  2. **都會紅狐染疫警戒**：阿德萊德都市紅狐染疫引發「全澳都會生物安全 Rethink Moment」（垃圾桶上鎖、廚餘管理、防範接觸後院兔寵/犬貓）。
  3. **NSW 塔隆加動物園 (Taronga Zoo) 疫苗試驗**：啟動瀕危/受脅鳥類 H5 疫苗試驗以收集抗體免疫數據。
  4. **BioResponse NSW 前線 App**：新州強制全州野外巡查員安裝專用應變 App，提供 24hr 動物疾病緊急專線 (1800 675 888)。

### 🦅 物種生態庫擴充與一鍵快篩強化
- **新增物種生態檔案**：於 `DEFAULT_SPECIES_PROFILES` 納入「赫頓鸌 (Hutton's Shearwater)」與「野生紅狐 (Red Fox)」。
- **一鍵快篩升級**：支援「🚨 新州 / 雪梨北灘 (NSW 22起)」、「🌊 赫頓鸌 / 瀕危留鳥 (科夫斯港)」等直觀篩選按鈕。

### ⚖️ 定量風險模型同步 (`risk_assessment.html` & `risk_assessment_en.html`)
- 更新 NSW 確診野生動物事件指標至 **22 起**。
- 地緣評估結論維持穩固：雪梨北灘與肯布拉港病例皆屬太平洋沿岸海灘，與內陸 Central West 高地之 Nestlé Purina Blayney 廠隔著藍山山脈天然屏障（直線距離 > 200 公里），商業原料供應鏈維持安全。

---

## [v2.8.1] - 2026-09-07

### 🚀 GitHub Actions CI/CD 自動化流程修復與 4 大雙語頁面全覆蓋
- **全面升級 `git add -A` 與 `git diff --cached` 提交機制 (`auto_update.yml`)**：
  - 改採 `git add -A` 自動暫存所有更新與新增檔案，徹底避免因個別檔名不存在導致 `git add` 中斷或暫存區為空 (`no changes added to commit`, exit code 1) 的問題。
  - 改以 `git diff --cached --quiet` 嚴謹檢測暫存區實質異動，有變動才執行 commit，杜絕空提交報錯。
  - Step 4b 補齊英文版 Live 頁面自動複製備份指令 (`cp index_en.html live_page_en.html`)。
- **4 大核心決策報告網頁與 Live 頁面全自動同步**：
  - 完整涵蓋 `index.html` (中文報告主頁)、`index_en.html` (英文報告主頁)、`risk_assessment.html` (中文風險評估) 與 `risk_assessment_en.html` (英文風險評估) 及對應 Live 備份頁。
- **16:9 簡報投影片與歷史週報歸檔庫自動推送**：
  - 自動納入 `h5n1_weekly_slides.html` (週報簡報)、`risk_assessment_slides.html` (中文風險評估簡報)、`risk_assessment_slides_en.html` (英文風險評估簡報) 及 `weekly_reports/` 歸檔資料夾，確保前端 Modal 彈窗與簡報連結維持 100% 可用。

---

## [v2.8.0] - 2026-09-07

### 🦅 eBird 雙軌 GIS 地圖圖層與實測點位 (`risk_assessment.html` & `risk_assessment_en.html`)
- **實態野鳥觀測點位圖層 (`🦅 eBird 實態點位`)**：
  - 於 Leaflet 地圖上直接繪製全澳 129 筆亮青色脈衝圓圈點位，點擊或懸停可完整查閱物種 (`comName`)、地點 (`locName`)、實際目擊數量 (`howMany` 隻) 與觀測時間 (`obsDt`)。
- **地圖節點 Tooltip 雙軌比對 (Model Projected vs eBird Observed)**：
  - 大候鳥停歇光圈（如莫頓灣 Moreton Bay、獵人河口 Hunter Estuary 等）懸停 Tooltip 同時呈現「📊 模型預估滯留量」與「🦅 eBird 30天周邊 220km 實測目擊數量與筆數」。
- **地圖內 Top-Left 雙軌 HUD 儀表板**：
  - 實時呈現模型預估滯留總量 (2.2M AU / 600K NSW) vs eBird 近期實測數據 (129 筆觀測, 1,480+ 隻野鳥)。

### ⚡ 免 fetch 零 CORS 阻擋靜態打包 (`assets/js/bird_data.js`)
- `h5n1.py` 自動將 eBird 數據打包寫入 `assets/js/bird_data.js` (`window.ebirdDataEmbedded`)，徹底解決 Windows 本機檔案直接點開 (`file://`) 時瀏覽器跨域 `fetch` 阻擋造成的「載入中...」現象，開檔即可順暢渲染。

### 📅 當前月份動態對齊與面板切換
- 風險評估網頁改為依據系統當前日期 (`new Date().getMonth()`) 動態決定預設月分（例如 9/7 開啟自動預設為 **9 月**），並提供 `[當前月份 (Sep)]` 與 `[🔥 10月 (年度高峰)]` 快捷按鈕。
- 切換月份時，地圖 HUD 面板模型的預估滯留量與地圖熱點光圈隨之即時響應。

### 🌐 疫情監控網頁英文版 eBird 組件同步 (`index_en.html` & `report_template_en.html`)
- 於 `report_template_en.html` 嵌入英文版 `eBird API v2 Live Field Sightings Feed` 即時遙測看板，編譯生成 `index_en.html`，達成疫情監控網頁中英文門戶 100% 雙語完全同步。

### 📂 週報簡報歸檔與時間軸獨立解耦
- 疫情週報 (`h5n1_weekly_report_*.html`) 歸檔與風險評估簡報 (`risk_assessment_weekly_*.html`) 歸檔於各自網頁彈窗獨立呈顯。
- 採 ISO 週一邊界演算法 (`YYYYMMDD_YYYYMMDD`) 計算檔案保存區間，徹底避免同週每日多餘測試檔殘留。

### 📊 權威數據對齊 (DAFF 2026-09-07)
- 全澳確診事件總數同步至 **484 起**（包含 1,273 起排除案件與 34,358 筆熱線通報）。

---

## [v2.7.0] - 2026-09-04

### 🦅 野鳥與候鳥生態即時 API 整合 (eBird API v2 & ALA Backup)
- **eBird API v2 實時數據串接 (`fetch_ebird_data()`)**：
  - 透過 GitHub Secret (`EBIRD_API_KEY`) 安全注入，Server-side 爬取全澳 6 州（NSW、SA、WA、VIC、QLD、TAS）近 30 天內高風險水鳥與候鳥觀測紀錄。
  - 成功過濾 129 筆高風險物種目擊（銀鷗、鳳頭燕鷗、太平洋黑鴨、鸕鶿、蒼鷺等），輸出靜態 `bird_data.json`，金鑰永不外洩於前端。
- **Atlas of Living Australia (ALA) 免 Key 數據備援 (`fetch_ala_data()`)**：
  - 整合 `biocache.ala.org.au` REST API 檢索全澳 35,000+ 個生態調查點（含 Birdata、iNaturalist AU、澳洲博物館等），生成 `ala_bird_data.json`。
- **四層全維度數據備援體系 (4-Tier Data Fallback System)**：
  - **Tier 1 (主要官方)**：DAFF 官網 `curl_cffi` 擬真爬蟲與 Playwright WAF 繞過。
  - **Tier 2 (即時新聞)**：Google News RSS 動態關鍵字新聞流。
  - **Tier 3 (本地數據庫)**：`cases_events.json` 468+ 起歷史事件與自動補全對齊演算法。
  - **Tier 4 (生態 API)**：eBird API + ALA 生態資料庫實時動態。

### 📐 定量風險評估儀表板與排版優化 (`risk_assessment.html` & `risk_assessment_en.html`)
- **重返時間軸估算標籤更正**：將重返視窗估算器（Re-entry Window Estimator）中容易混淆的「6 階段 / 6-Stage」標籤更正為「3 情境 / 3-Scenario」（最樂觀 45 天、基準 90 天、極端 180 天）。
- **標頭換行適配**：在「模型/Model」前加入 `<br>` 換行，改善中英文版頂部視覺對稱性。

### 📊 最新權威數據對齊 (DAFF 2026-09-04)
- 全澳確診事件總數同步至 **468 起**（包含自動完成之 SA +1、VIC +5、NSW +4、TAS +2 案件對齊）。
- 州別數據：南澳 263 起、維州 148 起、塔州 25 起、NSW 20 起、西澳 10 起、昆州 2 起。
- 商業家禽、蛋場與乳牛場維持 **100% 完美零確診 (Area Freedom)**。

---

### 🗓️ 候鳥遷徙時間軸卡片 (Migratory Bird Seasonal Risk Timeline)
- **補回並獨立升級「候鳥遷徙回澳洲時間軸與高風險期動態評估」專區**：在 `report_template.html` 與 `index.html` 的「受影響野生鳥類物種與生態生物安全指南」專區內，補回 4 階段時間軸評估卡片：
  - **8 月下旬 (前鋒期)**：成年海鳥 (棕賊鷗/巨鸌) 前鋒抵達，造成目前全澳確診爆發與海獅/海豚感染。
  - **9 月 (☠️ 極高風險起點)**：200 萬隻、36 種國際候鳥大部隊正式登陸澳洲北部。
  - **10 月 (🔴 全國疫情地雷期)**：候鳥群自北部向全澳洲內陸溼地、灌木叢及東南沿海 (NSW/VIC/SA) 大規模分散。
  - **11 月~隔年 2 月 (高峰停留期)**：候鳥群留留在各地過冬覓食，至隔年 3 月集體北返。

---

### 📺 介面與導航功能 (UI & Navigation Enhancements)
- **主頁頂部雙功能按鈕**：在 `index.html` 與 `report_template.html` 頂部 Sticky Header 新增 `📺 16:9 週報簡報 (Slides)` 與 `📂 歷次週報歸檔` 雙功能控制鈕。
- **歷次週報歸檔 Modal 彈窗 (`toggleArchiveModal()`)**：點擊按鈕跳出彈窗，可線上直接瀏覽並開啟 `weekly_reports/` 資料夾內所有歷史每週簡報。

### 🤖 Gemini AI 全網情報整合與 404 Fallback 模型名稱修復 (Gemini AI Grounding & Bug Fix)
- **修復 Gemini API 404 模型無效報錯**：修復 GitHub Actions 紀錄中 `gemini-2.5-flash-lite` 與 `gemini-2.5-pro` 回傳 HTTP 404 找不到模型的錯誤，修正備援模型鏈為官方有效模型：`gemini-2.5-flash` ➔ `gemini-2.0-flash` ➔ `gemini-1.5-flash` ➔ `gemini-1.5-pro`。當主力模型遇 429 限流時可無縫切換備援模型。
- **實時新聞與政策 AI 檢索 (`analyze_new_species_with_gemini()`)**：整合 Gemini API Google Search Grounding，自動搜尋 DAFF 未包含之新聞、各州政策（如 NSW DPIRD 海灘遛狗繫繩、後院養雞圈養）、離島撤離與哺乳類病例。
- **動態歸檔清單生成器 (`generate_dynamic_weekly_archive_html()`)**：在 `h5n1.py` 中自動掃描 `weekly_reports/` 資料夾，自動解析日期區間檔名並生成響應式 HTML 卡片供 Modal 彈窗調用。

### 📊 最新數據對齊 (Data Updates)
- 全澳確診事件總數同步至 **456 起**（一週內激增 +147 起）。
- 州別數據：南澳 267 起、維州 140 起、塔州 20 起、NSW 17 起、西澳 10 起、昆州 2 起。
- 商業家禽、蛋場與乳牛場維持 **100% 完美零確診 (Area Freedom)**。

---

## [v2.6.0] - 2026-09-02

### ⚖️ H5N1 定量風險評估模型儀表板 (`risk_assessment.html`)
- **全新定量風險模型 (Quantitative Risk Score, 0 ~ 100 分)**：針對台灣團隊評估重啟澳洲 Nestlé Purina Blayney 廠寵物食品進口、擔憂 TW APHIA 宣告 NSW 為疫區之需求，建立 5 大維度動態權重算式：
  - $S_{housing}$ **政策與物理隔離 (25%)**：強制圈養令、物理防鳥網與水質消毒。
  - $S_{migratory}$ **候鳥遷徙與季節重疊 (20%)**：4 階段遷徙時間軸與 NSW 濕地水體重疊性。
  - $S_{vector}$ **跨物種傳播與哺乳類向量 (20%)**：南澳紅狐/海豚個案與陸生野生腐食動物夜間侵入禽舍風險。
  - $S_{virology}$ **病毒株傳播學 (15%)**：H5N1 Clade 2.3.4.4b 低溫耐受度、潛伏期 (1-3天) 與排毒量。
  - $S_{proximity}$ **地緣距離與商業零確診 (20%)**：全澳商業禽場 0 宗感染與距 Blayney 工廠 215 km 距離。
- **70/30 雙軌校準對照專區 (Dual-Track Calibration)**：
  - **全球 H5N1 Clade 2.3.4.4b 歐美經驗 (70%)**：判定病毒跨物種感染力與遠洋野鳥帶毒特性。
  - **澳洲本土 H7 歷史爆發軌跡 (30%)**：判定澳洲地理孤立性、州政府 2~4 週快封快切效率與 TW APHIA 歷史邊境封鎖慣例。
- **互動式敏感度模擬器 (Interactive Risk Simulator)**：內建 Chart.js 5 維度雷達圖 (Radar Chart)、參數下拉選單、商業禽場爆發開關與距離滑桿。

### 🌐 英文版全功能動態儀表板 (`index_en.html` & `report_template_en.html`)
- **英文獨立模板 (`report_template_en.html`)**：完整翻譯主儀表板所有專區、KPI 卡片、物種生態評估卡片、時間軸與表格欄位，專供寄送給國外同事與全球 Purina 團隊。
- **Python 自動化雙語編譯 (`h5n1.py`)**：每次執行連網抓取數據時，自動同時編譯產出 `index.html` (中文) 與 `index_en.html` (英文) 以及 `live_page_en.html`。
- **頂部 Header 導航切換**：在所有網頁頂部 Sticky Header 加入 `🌐 English Version` / `🌐 中文版` 與 `⚖️ Risk Model` 快速導航控制鈕。

---

## [v2.5.1] - 2026-09-02

### 📂 資料夾留檔機制 (Weekly Report Archiving)
- **建立 `weekly_reports/` 歷史週報歸檔資料夾**：
  - 每週自動留檔存檔簡報，檔名加入精確日期區間（例如：`weekly_reports/h5n1_weekly_report_20260824_20260902.html`）。

---

## [v2.5.0] - 2026-09-02

### 🌟 新功能 (New Features)
- **16:9 Web Presentation Deck 網頁簡報系統 (`h5n1_weekly_slides.html`)**：
  - 新增 16:9 可簡報之網頁投影片，專為 2026.08.24 – 2026.09.02 澳洲 H5N1 核心疫情週報設計。
  - 支援鍵盤快速鍵導航 (`←`/`→`/`Space`/`PageUp`/`PageDown`/`Home`/`End`/`F 全螢幕`)。
  - 9 頁故事線結構，包含數據變化、陸海哺乳類失守（海豚與紅狐）、南極科學基地緊急撤離、金島企鵝暴斃、新州防範指引與 16:9 每週趨勢動態圖表。

### 🐛 錯誤修復 (Bug Fixes)
- **疫情週次增長趨勢圖表時間軸修復 (Weekly Epi-Curve Fix)**：
  - 修復 `report_template.html` 與 `index.html` 每週長條圖 (`eventTrendChart`) 寫死標籤止於 `8月W2` 導致 8月W3、8月W4、8月W5 與 9月W1 確診數據無法顯示且造成 8月W1 數據異常膨脹的問題。
  - 實作 `generateWeekLabels()` 動態時間軸生成器，自動擴充 X 軸標籤至當前最新週次 (`9月W1`)。
