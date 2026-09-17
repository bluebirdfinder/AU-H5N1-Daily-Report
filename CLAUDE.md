# CLAUDE.md — 澳洲 H5N1 疫情監控與 Nestlé Purina Blayney 風險評估系統

本檔案給每次在此 repo 工作的 Claude 讀。專案背景、核心規則、已知資料完整性陷阱都寫在這裡，避免重蹈覆轍。

## 專案是什麼

雙產出的靜態網站系統，服務對象是評估 Nestlé Purina Blayney 廠（NSW）寵物食品原料供應鏈風險：

1. **疫情監控頁**（`index.html` / `index_en.html`）— 由 `h5n1.py` 執行 `compile_template()` 從 `report_template.html` / `report_template_en.html` **動態編譯**產生，每天兩次由 `.github/workflows/auto_update.yml` 自動跑。
2. **風險評估頁**（`risk_assessment.html` / `risk_assessment_en.html`）— **不是**模板編譯產物。`h5n1.py` 只有 `sync_risk_assessment_weekly()` 會碰它，且只改「歷次週報歸檔」彈窗的連結。其餘內容以前是人工手改的靜態 HTML，**2026-09-16 已改為讀取 `assets/js/cases_events.js`（`window.casesEventsEmbedded`）在載入時動態校正**（見下方「已修復」），但候鳥數字與部分敘述文字仍是靜態，改動前務必先看下面的清單。

**這個「一個全自動、一個半自動」的落差是本專案最大的資料完整性風險，修改前必讀。**

## 最高指導原則（來自 AGENT.md，勿違反）

- 台灣 BAPHIQ 檢疫是以「州（State）」為封鎖單位。NSW 境內**任一**商業家禽場確診 = 全州立即封鎖，與距離 Blayney 廠幾公里無關。
- 風險評估錨點必須是「NSW 商業家禽 0 確診」與「野鳥是否外溢至 NSW 商業聚落」，嚴禁用物理距離模糊焦點。
- 候鳥數據（eBird/Movebank/GBIF/ALA）是領先指標，不是終點指標；真正的紅線永遠是 NSW 商業場是否確診。

## 2026-09-16 稽核與修復摘要

### 已修復（程式碼層級）

1. **`h5n1.py` 新增 `write_cases_events_js()`**：每次編譯都把 `official_stats`（跟 `index.html` 的 `window.OFFICIAL_STATS` 同一份資料）寫到 `assets/js/cases_events.js`（`window.casesEventsEmbedded`）。`risk_assessment.html`/`_en.html` 原本就寫了讀這個全域變數的程式碼（`syncTimelineDataWithLiveStats()`），但從未有檔案真正賦值它，是死綁定——現在補上了。
2. **`parse_daff_official_stats()` 的離線 fallback 從寫死字典改為真的重新計算**：DAFF 官網連不上時，以前永遠退回函式最上方寫死的舊字典（長期停在 484 起/NSW 22 起）；`compute_stats_from_cases()`（用 `cases_events.json` 重新統計的權威回退方案）明明就存在，卻從來沒被呼叫過。現在 DAFF 連不上時會先呼叫它，用資料庫自己的最新內容回推，不會再退回好幾週前的數字。
3. **`risk_assessment.html`/`_en.html` 新增 `syncCaseEventsFromEmbedded()`**，在 `window.addEventListener('load', ...)` 第一步執行，把 NSW 卡片（`#kpi-nsw-events-val`）、科學矩陣的 NSW/VIC/SA 數字、`select-nsw-events` 下拉選單文字與分數分級、方法論 Modal 裡的「484 起」等全部改為讀 `window.casesEventsEmbedded` 動態產生，不再是寫死文字。
4. **`onload` 初始化鏈改成逐步 `try/catch`**：稽核時用 Playwright 實測發現，只要 Chart.js CDN 被擋（企業防火牆常見情境，這也是本專案自己在 README 反覆提到的痛點），`initRadarChart()` 一拋錯就會讓同一個監聽器裡後面所有步驟（包含決定風險分數的 `recalculateRisk()`）整串不執行，NSW 卡片、風險分數、Decision Zone badge 全部停在初始靜態值。現在每一步獨立 `try/catch`，一步失敗不影響其他步驟。
5. **`total_birds` 欄位名 bug**：`risk_assessment.html`/`report_template.html` 多處讀 `state_summary.NSW.total_birds`，這個欄位在 `bird_data.json` schema 裡不存在，永遠 fallback 到寫死值。已改為對 `high_risk_observations` 現場 `reduce` 加總（跟 `renderEbirdOnMap()` 原本就寫對的邏輯一致）。
6. **`report_template.html` 補上 `#ebird-total-obs`（首頁候鳥總數大字）的 JS 綁定**：以前完全沒有綁定，永遠顯示編譯當下的靜態文字。
7. **候鳥資料新鮮度警示**：`bird_data.json` 的 `fetched_at_utc` 超過 2 天沒更新時，兩個頁面都會顯示「⚠️ 資料已 N 天未更新」，不再讓使用者誤以為數字是即時的。
8. **雜項一致性修正**：Decision Zone Matrix 的「當前現況」註記改成動態貼到真正對應的分數區間卡片上（含 `isCommercialFarmInfected` 觸發時強制標在紅色區）；「商業禽場爆發 (+75分)」按鈕文字改成「強制封頂 100分」以符合 `recalculateRisk()` 的實際邏輯；Card 2（商業家禽與蛋場狀態）改成會跟著模擬器的商業禽場爆發開關變色，不再永遠顯示綠色安全；移除 `report_template.html`/`_en.html` 對 `gbif_bird_data.js`（193KB）的死重量載入（該頁從未讀取它）；ZH 版工廠地緣距離卡片補上 `MIN_DISTANCE_PLACEHOLDER`（EN 版本來就有，ZH 版之前漏掉，永遠顯示寫死的「215 公里」與具體卻可能過期的地名）。
9. **`call_gemini_api_with_retry()` 備援模型清單全滅（連續修過兩輪）**：真實環境 GitHub Actions log 證實 `gemini-2.0-flash`/`gemini-1.5-flash`/`gemini-1.5-pro` 三個備援模型全部回 404「no longer available」。第一輪改成 `gemini-2.5-flash` → `gemini-2.5-flash-lite` → `gemini-2.5-pro`，結果同一天 2 小時後再測，`gemini-2.5-flash-lite`/`gemini-2.5-pro` 兩個也雙雙回 404「no longer available to new users」——Google 端下架速度快到「剛修好就又壞」，具名備援模型清單本身就是不可靠的策略。**最終做法（現狀）：不再猜測其他具名模型，`models` 清單改成 `["gemini-2.5-flash", "gemini-2.5-flash"]`，也就是唯一經真實環境反覆驗證有效的模型重試兩次**，見 `h5n1.py` 第 530 行附近的說明註解。往後若這個模型也開始 404，不要再猜新模型名稱，先用真實 log 確認可用的模型再改。
10. **`fetch_movebank_data()` 從未真正呼叫過 Movebank API（已確認，非推測）**：舊版只依 `MOVEBANK_USER`/`MOVEBANK_PASSWORD` 環境變數是否存在印一行狀態訊息，實際永遠寫死 `AUSTRALIAN_STUDY_TRACKS`（6 條航跡，日期凍在 2026-08-01~09-08，跟「651 隻候鳥」凍結問題是同一類「看起來像即時、實際是死資料」陷阱，只是這次連 log 都沒老實說）。使用者確認持有真實 Movebank 帳密後，已改為呼叫新函式 `fetch_movebank_live_tracks()`：
   - 用 `entity_type=study` 抓可存取研究清單，依「名稱含 Australia/Australian（+100）> `main_location_lat<0` 南半球（+20）> 物種關鍵字命中海鳥/涉禽（+10）> 有下載權限（+5）」排序，取前 10 個候選，避免抓到象海豹、食蟻獸等跟澳洲候鳥完全無關的研究。
   - 實作 Movebank 的**授權條款自動同意流程**：`_movebank_get()` 內部若第一次請求回傳的不是 CSV（代表伺服器回的是授權條款全文，HTTP 200 或 403 皆可能），會對該回應內文算 `hashlib.md5`，帶著 `license-md5=<hash>` 重送同一請求，即可解鎖真正資料——這是 Movebank API 官方協議，不是繞過驗證。
   - 輸出 JSON 新增 `is_live_data: bool` 欄位與對應 `source` 文字，`report_template.html`/`risk_assessment.html` 的候鳥走廊區塊已綁定這個欄位動態顯示「即時連線」或「範例資料」，不再永遠寫死顯示「Live GPS」。
   - **真實環境驗證結果（2026-09-16，run 35100408995）**：授權自動同意流程本身運作正常，log 可見多筆 `自動同意授權條款後成功取得資料 (license-md5 已接受)`（Nankeen Kestrels South Australia、Green python Cape York、Christmas Island flying fox、Swamp wallabies Phillip Island、humpback whales east coast、Western Ringtail Possum、Juan Fernández Petrel、Indian yellow-nosed albatross Amsterdam Island、ICARUS Seychelles Sooty terns 等）——但每一個都緊接著 `解析出 0 個個體，0 條有效航跡`，代表這個帳號目前排到的可讀 study 近 30 天內都沒有任何個體回傳 GPS 座標（很可能是已結束的歷史研究專案，不是程式邏輯錯誤）。系統會如預期安全退回範例資料（`is_live_data: false`），不會顯示假的「即時」標籤。
   - **排序權重修正 (第三輪，2026-09-16)**：上述測試結果本身就暴露了排序邏輯的問題——`Australia` 字樣權重（+100）遠高於物種關鍵字（+10），導致 Water buffalo/Swamp wallabies 這種名稱含 Australia 但跟候鳥完全無關的研究排到前面。使用者直接在 Movebank 官網（movebank.org）用 taxon search 找到 3 個貨真價實的東亞—澳大拉西亞遷飛區 (EAAF) 候鳥研究：`Tracking Curlew sandpipers/Great Knots/Red-necked stints along the EAAF`——名稱完全沒有 Australia 字樣，卻是本專案風險物種清單裡的核心物種（大濱鷸、紅頸濱鷸都在 GBIF 的 `HIGH_RISK_SPECIES` 學名清單裡）。已重新調整權重：使用者驗證過的研究名稱給保證最高分（+1000）；`EAAF` 關鍵字次高（+50）；物種關鍵字權重從 10 提高到 30；`Australia` 字樣權重從 100 大幅降到 15（只當次要加分）。**同時修掉一個會讓這 3 個研究永遠進不了候選池的邏輯錯誤**：`pool = downloadable or visible_only` 是 Python `or` 短路邏輯，只要帳號名下有任何一個有完整下載權限的 study（即使跟候鳥無關），`visible_only`（只能看中繼資料、需另外申請下載權限的 study）就整組被忽略——但這 3 個 EAAF 研究很可能正是這種需要另外申請的類型（Movebank 網頁上顯示「Contact owner」）。已改為兩邊取聯集（依 study id 去重）。**尚未在真實環境驗證**（沒有 Movebank 帳密的沙盒環境只能確認語法與計分邏輯正確，無法確認這 3 個 study 最終是否真的能透過 license-md5 流程拿到資料，或需要使用者先跟 study 擁有者申請權限）。
11. **⚠️ `h5n1_weekly_slides.html`（疫情週報簡報）與 `risk_assessment_slides.html`/`_en.html`（風險評估模型週報簡報）從未被本輪任何一次稽核觸及，是全新發現的死角，且已修復**：這三份 16:9 簡報檔案完全獨立於 `index.html`/`risk_assessment.html`，`sync_weekly_slides()`/`sync_risk_assessment_weekly()` 每週一自動跑，但**只做「歸檔」跟「把封面日期區間文字換掉」**，完全不校正內容數字。稽核發現：
    - `h5n1_weekly_slides.html` 內容最後一次真正修改是 2026-09-14（`git log` 證實），完全沒有讀取任何 JSON/JS 資料，NSW「22 起」、全澳「484 起」、陰性排除「1,273 起」、熱線通報「34,358 筆」、SA/VIC/TAS/WA/QLD 各州數字全部寫死在 HTML 裡，跟今天在主頁面修過的「死綁定」是同一類問題，只是這次連綁定的嘗試都沒有。
    - `risk_assessment_slides.html` 唯一一處試圖讀 `casesEventsEmbedded` 的程式碼（時間軸圖表當前點）寫的是 `Array.isArray(window.casesEventsEmbedded)`——但這個變數實際上是物件不是陣列，判斷永遠是 `false`，是**跟 `risk_assessment.html` 的 `syncTimelineDataWithLiveStats()` 同一種「假設錯誤資料型態」bug**，圖表當前點永遠停在寫死的 `498`。KPI 卡片「NSW 全州野鳥確診事件」的「22 起事件」中英文版都是純靜態文字，完全沒有綁定。
    - **修復方式**：三個檔案都加上 `<script src="assets/js/cases_events.js">`（`h5n1_weekly_slides.html` 原本完全沒有引入任何 embedded JS）；用 `data-bind="total-events"`/`nsw-events`/`sa-events`/... 等屬性標記所有「當前累計數字」，載入時用一個小函式統一查詢並覆寫；`risk_assessment_slides.html` 的 `Array.isArray` 誤判改為直接讀 `.total_events`。已用 Node Playwright 對 `file://` 直接開檔驗證：`h5n1_weekly_slides.html` 全澳 551/NSW 32/SA 299/VIC 169/TAS 38/WA 10/QLD 2/陰性排除 2,450/熱線通報 45,115 全部正確跟 `assets/js/cases_events.js` 一致；兩份 `risk_assessment_slides*.html` 的 KPI 卡片也正確顯示 32 起/32 Events。
    - **刻意不修的部分**：像「由上週 17 起增至 22 起」「單週激增 +137 起」「自上週一 (8/24) 約 347 起爆發增長至 484 起」這類**週間比較敘述文字**維持原樣不自動改寫——這個專案沒有可靠的「上週總數」資料來源，硬猜一個「上週數字」會製造出看起來精確、實際是編造的假趨勢敘述，風險比維持一句過期但至少誠實的舊敘述更高，屬於商業/編輯決策而非程式 bug，留給人工每週手動更新這段敘述文字。

驗證方式：以 Node Playwright（`file://` 直接開檔）逐一讀取上述 DOM 元素文字並比對 `cases_events.json`/`bird_data.json` 重新算出的 ground truth，確認一致；另外用 `setCommercialFarmStatus(1)` 模擬商業禽場破口情境，確認 Card 2、Decision Zone badge、風險分數三處連動正確；Movebank 授權流程用本地 mock `requests.get` 單元測試過 accept/retry 邏輯，並在真實 GitHub Actions 環境跑過確認 log 行為與程式碼邏輯一致。

### 尚未修復，需要人工決定或無法在此環境驗證

1. ~~**`EBIRD_API_KEY` 這個 GitHub Secret 從未設定過**~~ **（2026-09-16 已由使用者於 GitHub Secrets 補上，並經真實環境驗證修復）**：舊 log 證實 `[eBird API] 未設定 EBIRD_API_KEY 環境變數，跳過候鳥數據抓取`，`bird_data.json` 的「651 隻」是 2026-09-07 一次性手動上傳快照，從未被自動化真正抓過。使用者新增 Secret 後，最新一次真實 Actions 執行（run 35100408995 前後）確認 eBird API 抓取成功，回傳 151–158 筆新鮮的高風險觀測記錄，`bird_data.json` 的 `fetched_at_utc` 已能正常每次更新，不再凍結。
2. ~~**`ala_bird_data.json` 從未產生過**~~ **（2026-09-16 已修復，尚待真實環境驗證）**：根因是 `fetch_ala_data()` 用裸 `requests.get()`，被 `biocache.ala.org.au` 的 WAF 直接判定為爬蟲回傳 HTTP 403。已改為呼叫 `smart_fetch_url()`，走跟 DAFF 同一條「curl_cffi Chrome 指紋擬真 → CF Worker 代理 → 真實 Playwright 瀏覽器 → 純 requests」四段降級鏈；並在收到 Playwright 回傳的 HTML 包裝 JSON（`<pre>...</pre>`）時自動剝殼解析。**修復途中另外發現並修掉一個更底層的 bug**：`playwright_fetch_url()` 在一般網址導航情境下（未傳入 `html_content`）永遠 `return html_content`（也就是永遠回傳呼叫時傳入的 `None`），而不是回傳它自己抓到、存在 `fetched_html` 變數裡的真實內容——這代表 `smart_fetch_url()` 的「真實瀏覽器」防線，包括原本 DAFF 也在用的那條，一直以來對「導航到目標網址」這種一般用法都是死的，只有靠前面 curl_cffi 那一段先成功才會被誤以為整條鏈有效。此 bug 已修（改為 `return fetched_html`），理論上同時提升了 DAFF 抓取的韌性，但兩者都還沒有機會在真實 GitHub Actions 環境跑一次驗證（沒有 curl_cffi/Playwright 的沙盒環境只能確認不會 crash，無法確認真的抓得到 ALA 資料）。~~**已知限制**：即使抓取修好，目前 repo 裡沒有任何一個 `assets/js/*.js` 或 HTML 頁面讀取 `ala_bird_data.json`~~ **（2026-09-17 已補上前端綁定，見下方同日期章節）**：`risk_assessment.html`/`_en.html` 已加上 `assets/js/ala_bird_data.js` 與 `renderAlaOnMap()`，抓取失敗時會安全隱藏而非顯示假的 0 筆資料；但抓取端本身在真實環境仍持續失敗（WAF 擋 GitHub Actions IP），所以目前地圖上實際還看不到 ALA 圖層，只是「資料一旦能抓到就會自動顯示」，尚未有機會用 `available:true` 的真實資料驗證圖層渲染是否正確。
   - **真實環境驗證結果（2026-09-16，run 35122363227）**：`playwright_fetch_url()` 的 bug 修復本身已證實有效——同一次執行裡 DAFF（37,551 字元）、NSW/WA/TAS 州政府頁、Google News RSS 全部透過 curl_cffi 成功；SA/VIC/QLD 政府頁則是 curl_cffi 失敗、CF Worker 失敗後，真的靠 Playwright 拿到 15~25 萬字元的真實內容（過去這條路徑是死的，永遠 None）。但換到 `biocache.ala.org.au` 時，curl_cffi 靜默失敗（沒印出任何訊息，可能是回應太短沒進判斷式）、CF Worker 回 503，Playwright 導向後**只拿到 195 字元**——遠低於 `smart_fetch_url()` 內建的「回應需 > 500 字元才採信」門檻，因此正確地被判定為不可信內容而放棄，`requests` 最後一段大概率再次被拒。195 字元太短，不可能是真正的候鳥觀測 JSON（就算查無資料也會是幾十筆欄位的結構），比較可能是 WAF 針對 GitHub Actions 的 IP 網段直接回傳一個極簡拒絕頁/錯誤訊息，**擋的是來源 IP，不是瀏覽器指紋**，所以就算換成真的無頭瀏覽器也一樣被擋。結論：`smart_fetch_url()` 本身這次證實修對了（DAFF 等既有用途因此更穩），但 ALA 這個資料源目前在 GitHub Actions 執行環境下仍然抓不到，是否要再花時間試其他繞法（例如自架代理、換不同 CF Worker 路由）留給使用者決定是否值得投入。
3. **⚠️ `assets/js/purina_auth.js` 的「機密存取」密碼門完全是裝飾性的，不是真的資安控制（repo 已確認是 public）**：查過 `api.github.com/repos/bluebirdfinder/AU-H5N1-Daily-Report`，`private: false`——不是「如果公開」，是確定公開。這支檔案在前端硬編碼了明碼密碼清單，且驗證邏輯只是在頁面上蓋一層視覺遮罩（overlay），**底層 DOM 內容從頭到尾都完整存在，沒有被移除或加密**——稽核時用 Playwright 直接讀 DOM 就拿到全部風險評估數字，完全不需要通過這個「密碼驗證」；密碼本身也進了 git 歷史，就算之後改掉，舊 commit 仍查得到。任何人打開瀏覽器開發者工具、`view-source`、或直接 `curl` 都能看到頁面宣稱的「商業機密與未公開流行病學遙測數據」，密碼門形同虛設，而且「每月換密碼」這種做法對這個漏洞沒有實質幫助（擋的是「按驗證鈕」這個動作，不是「拿到資料」這件事）。這不是程式碼稽核要修的範圍，是商業/架構決策：要嘛不再宣稱「機密」，要嘛認真做私有網站/伺服器端驗證，使用者已知悉、留待內部討論後再處理。

**教訓**：往後任何「這個數字對不對」的問題，先用 `python3` 對 `cases_events.json` / `bird_data.json` 重新算一次 ground truth，不要只看 HTML 顯示的字。畫面好看 ≠ 數字是活的；有 `id` 也不代表真的有 JS 在寫它，要親自 grep 確認賦值那一行存在。

## 2026-09-17：高風險候鳥物種清單擴充（依官方權威來源，非隨口列的清單）

使用者親自在 Movebank 上找到 3 個真正相關但清單漏掉的 EAAF 候鳥研究後，追問「候鳥物種清單有沒有漏」，進而要求依 WOAH/澳洲官方來源重新核對。此環境的網路政策擋掉了 `dcceew.gov.au`/`wildlifehealthaustralia.com.au`/`birdlife.org.au`/`woah.org` 等網域（`WebFetch` 全部回傳 `EGRESS_BLOCKED`，且 `/root/.ccr/README.md` 明確說這是組織政策、不可繞過），改由使用者直接貼上兩份官方文件全文：

1. **Wildlife Health Australia《Avian influenza in wildlife in Australia》Fact Sheet（2026-09，v5.2）**：確認雁形目（Anseriformes：鴨/天鵝/雁）與鴴形目（Charadriiformes：鷗/燕鷗/鷸鴴）是所有 AIV 的天然宿主——跟現有清單的「目」層級選擇方向一致。關鍵細節：**澳洲本土雁鴨科不會遷徙出境**，真正把病毒帶進澳洲的是三條路徑：① 每年 8-11 月從北半球遷徙來的鴴形目候鳥、② 常年從澳洲以北進入的雁鴨科、③ 常年從南極/亞南極遷徙來的海鳥（賊鷗、鸌）。此文件沒有列出具體物種清單。
2. **DCCEEW「H5 bird flu and native species」+ BirdLife Australia／Charles Darwin University 聯合《國家風險評估》報導**：明確點出方法論陷阱——國家風險分數 = 易感性（susceptibility）+ 脆弱性（vulnerability，滅絕風險），**兩者混在一起，不能直接當「監測用的高風險物種清單」使用**。原文自己警告：劍尾鸚鵡、須冠蜜鳥、平原走鴴這些極危陸鳥雖在「高風險」清單上，但「不太可能暴露於病毒或傳播病毒」，純粹因族群小、一感染就可能滅絕才上榜。真正該採用的是文中明確點名「易感性高、會傳播病毒」的物種：**黑天鵝（Black Swan）、麥雞鵝（Magpie Goose）**（澳洲鵜鶘已在清單）。Christmas Island Frigatebird、Abbott's Booby、Heard/Macquarie Island Imperial Shag 等「極度風險」物種**刻意不採用**——牠們風險分數主要來自「單一離島繁殖地」的脆弱性，地理上侷限在偏遠外島，跟 NSW/Blayney 廠風險路徑關聯低。

**已修改**：`h5n1.py` 三處物種清單都補上——GBIF 的 `HIGH_RISK_SPECIES`（學名精確清單）新增 `Calidris ferruginea`（尖尾濱鷸，使用者親自在 Movebank 找到的 EAAF 旗艦候鳥，原本只能靠關鍵字間接抓到）、`Cygnus atratus`（黑天鵝）、`Anseranas semipalmata`（麥雞鵝）；eBird 與 Movebank 的 `HIGH_RISK_SPECIES_KEYWORDS` 都補上 `"swan"`/`"goose"`（Movebank 另加 `"cygnus"`/`"anseranas"` 學名關鍵字）。**尚未在真實環境驗證**（下次自動排程或手動觸發 workflow 時才會實際查到這幾個新物種的觀測記錄）。

**方法論教訓**：往後任何「拿官方清單擴充物種清單」的請求，第一步永遠是先確認**這份清單衡量的是什麼**——「會不會滅絕」跟「會不會傳播」是兩個完全不同的問題，同一份報告混著兩者算出一個分數時，不能只看排名高低就照單全收，要找報告裡明確點出「這個物種易感性高/會傳播」的那一句話再採用。

## 2026-09-17：ALA 前端綁定補完、Movebank 排序修正真實環境驗證、Movebank 新增靜默失敗診斷

使用者把整個 repo 下載到本機 Windows 資料夾後，接續處理前一輪留下的三個「等你決定」事項，本輪先做前兩項：

1. **ALA 前端綁定（`risk_assessment.html`/`_en.html`）**：查 `gh run view` 真實 log 確認 `fetch_ala_data()` 目前**仍然**在每次 GitHub Actions 執行時失敗——`biocache.ala.org.au` 對 GitHub Actions 的來源 IP 網段回傳僅 195 字元的內容，未達 `smart_fetch_url()` 的可信度門檻，四段降級鏈全滅，跟 2026-09-16 稽核當時記錄的現象完全一致，**這是 IP 層級封鎖，不是程式碼問題，本次沒有再花時間嘗試繞過**。既然抓取端仍是死的，前端綁定改採「防禦性補完」而非模仿 GBIF 做一整塊新的資料源展示區：
   - `fetch_ala_data()` 改為無論成功或失敗都會寫出 `ala_bird_data.json` 與 `assets/js/ala_bird_data.js`（`window.alaBirdDataEmbedded`），失敗時內容是 `{"available": false, "unavailable_reason": "...", "observations": []}` 的空殼。修這個是因為原本失敗時完全不寫檔，一旦幫它接上 `<script src="assets/js/ala_bird_data.js">`，這支腳本在正式環境幾乎每次都會 404——現在保證檔案永遠存在，前端可以安全判斷 `available` 再決定要不要畫。
   - `risk_assessment.html`/`_en.html` 都加上這個 `<script>` 標籤，並新增 `renderAlaOnMap()`，把 ALA 觀測點畫成地圖圖層（跟既有 `renderGbifOnMap()` 同一套模式：`L.circleMarker` + `bindTooltip`），`data.available === false` 時直接 return，不畫假的「0 筆」空狀態。
   - 用本機 `python -m http.server` + Playwright 開真實 `http://localhost` 頁面（file:// 在部分瀏覽工具裡只會給靜態快照、不會真的執行 JS，踩過這個坑）驗證中英文兩版都能正確載入 `window.alaBirdDataEmbedded`（`available:false`）且 console 無錯誤。**尚未驗證的部分**：一旦 ALA 抓取真的成功過一次，`renderAlaOnMap()` 畫圖與 tooltip 排版是否正確，因為沙盒與真實環境目前都還沒有機會拿到 `available:true` 的真實資料可以實測。

2. **Movebank 第三輪排序修正——真實環境驗證結果**：拉 2026-09-17 00:19:17（run 35165871079）真實 log，確認排序權重修正確實生效：`Tracking Curlew sandpipers along the EAAF`（使用者親自在 Movebank 官網找到的 3 個 EAAF 研究之一）以 1100 分排名第一，證實「使用者驗證研究保證最高分」與「downloadable/visible_only 取聯集」兩處修正都正確把這 3 個研究送進了候選池最前面——**排序邏輯本身修對了**。但這 3 個研究目前實際下載會回傳 `<p>No data are available for download.</p>`，屬於 Movebank 資料源本身近期無回傳（study 沒有活體資料），不是程式邏輯錯誤，系統照設計安全退回範例資料（`is_live_data:false`）。
   - **順手發現的新異常**：40 分鐘後的下一次執行（01:00:20，run 35168581307）Movebank 回報「全站共 0 個 study」，跟同一天稍早的 8769 個天差地遠，且原本的程式碼在這種「請求技術上成功但解析出 0 筆」的情況完全不印任何診斷訊息，事後無法判斷是 Movebank 端暫時性異常還是回應格式真的變了。已在 `fetch_movebank_live_tracks()`（`h5n1.py` 第 2808 行附近）補上一行診斷：`studies` 解析為空時印出原始回應長度與前 200 字。**尚未驗證是否為一次性偶發**，下次排程執行後如果再次出現 0 個 study，這行新 log 才能告訴我們真正原因（例如 Movebank 帳號級 rate limit、或該端點確實偶爾回傳空 CSV）。

3. **修改前先 `git init` + 接上 GitHub remote**：使用者這次是把 repo 下載成本機一般資料夾（無 `.git`），既有的稽核方法（`git diff`/`git log` 比對）在這種狀態下用不了。已對本機資料夾執行 `git init`、`git remote add origin`、`git fetch`，並把 `HEAD` 指到追蹤 `origin/main` 的本機 `main` 分支（用 `git reset origin/main` 只動索引不動工作目錄，避免既有下載檔案被覆寫）。**教訓**：往後如果使用者說「我把檔案抓到本機資料夾」，先假設它不是 git repo，主動確認並重建 git 連線，不要預設 `git status`/`git diff` 這些指令能直接用。

**方法論教訓（本輪新增）**：修完程式碼後只要有跑過 `python h5n1.py`，即使是為了驗證語法／離線安全性，也一定要跑完就立刻 `git status` 檢查，把沙盒離線環境產生的降級資料（GBIF/eBird 用真實資料重新覆寫過的 `bird_data.json`/`index.html`/週報歸檔等）用 `git restore` 復原回遠端版本，只保留真正手動修改的檔案；不要假設「反正沒 commit 就沒事」，工作目錄裡混著降級資料本身就會讓下一個人（或下一次的自己）誤判現況。

## 開發規範

- CDN 白名單只能用 `cdnjs.cloudflare.com`，不可用 `cdn.jsdelivr.net` / `unpkg.com`（企業資安政策，見 AGENT.md）。
- 中英文四組檔案（`index`/`index_en`、`risk_assessment`/`risk_assessment_en`、`risk_assessment_slides`/`risk_assessment_slides_en`）必須維持同步；改一邊時記得另一邊——這次稽核發現的好幾個 bug 都是「中文版修過、英文版沒同步跟著改」（例如 NSW 事件數中文版寫 22、英文版某幾處寫的是完全不同的 17 或 456）。
- 改完 `h5n1.py` 或模板後，用 `python h5n1.py` 重新編譯，確認 console 印出「網頁自動編譯成功！」。在沒有 `EBIRD_API_KEY`/`MOVEBANK_USER`/網路權限的沙盒環境跑這支程式是安全的（每個抓取步驟都有 try/except 與離線 fallback），但跑完記得檢查 `git diff`，不要把沙盒才會出現的降級資料（例如網路不通導致 GBIF 寫出 0 筆記錄）誤 commit 回去。
- 需要稽核頁面數字或候鳥資料時，先用 `h5n1-data-audit` skill（`.claude/skills/h5n1-data-audit/SKILL.md`）。

## 檔案速查

| 檔案 | 角色 |
|---|---|
| `h5n1.py` | 抓取 + 編譯引擎，唯一會寫 JSON 資料檔、`index*.html` 與 `assets/js/cases_events.js` 的程式 |
| `report_template.html`/`_en.html` | `index.html`/`_en.html` 的原始模板（含 placeholder） |
| `risk_assessment.html`/`_en.html` | 風險模型頁，事件數字已動態化（讀 `cases_events.js`），候鳥數字/敘述文字仍多為靜態 |
| `cases_events.json` | 事件制病例資料庫（唯一 ground truth） |
| `assets/js/cases_events.js` | `cases_events.json`/`official_stats` 的免 CORS 打包版本（2026-09-16 新增），`risk_assessment.html` 靠這個檔案動態校正 |
| `bird_data.json` / `gbif_bird_data.json` / `movebank_tracks.json` | 三個候鳥數據源；eBird 已於 2026-09-16 補上 `EBIRD_API_KEY` 並驗證自動更新；GBIF 正常每日更新；Movebank 已串接真實 API + 授權自動同意流程，但目前排到的 study 均無近期活體航跡，故仍以標示清楚的範例資料 (`is_live_data:false`) 兜底 |
| `assets/js/*.js` | 上述 JSON 的免 CORS 打包版本，供 `file://` 離線開啟 |
| `h5n1_weekly_slides.html` | 疫情週報 16:9 簡報，`sync_weekly_slides()` 只改封面日期區間；事件數字 2026-09-16 已接上 `cases_events.js`（`data-bind` 屬性 + `syncWeeklySlideCaseEvents()`），週間比較敘述文字（「上週 X 起」）仍人工維護 |
| `risk_assessment_slides.html`/`_en.html` | 風險評估模型週報 16:9 簡報，`sync_risk_assessment_weekly()` 只改封面日期區間；KPI 卡片與時間軸圖表當前點 2026-09-16 已接上 `cases_events.js`（`data-bind="nsw-events"` + 修正 `Array.isArray` 誤判） |
