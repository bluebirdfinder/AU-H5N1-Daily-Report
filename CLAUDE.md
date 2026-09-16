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
   - **真實環境驗證結果（2026-09-16，run 35100408995）**：授權自動同意流程本身運作正常，log 可見多筆 `自動同意授權條款後成功取得資料 (license-md5 已接受)`（Nankeen Kestrels South Australia、Green python Cape York、Christmas Island flying fox、Swamp wallabies Phillip Island、humpback whales east coast、Western Ringtail Possum、Juan Fernández Petrel、Indian yellow-nosed albatross Amsterdam Island、ICARUS Seychelles Sooty terns 等）——但每一個都緊接著 `解析出 0 個個體，0 條有效航跡`，代表這個帳號目前排到的可讀 study 近 30 天內都沒有任何個體回傳 GPS 座標（很可能是已結束的歷史研究專案，不是程式邏輯錯誤）。系統會如預期安全退回範例資料（`is_live_data: false`），不會顯示假的「即時」標籤。**若使用者手上有已知目前仍在追蹤中的澳洲海鳥/候鳥 study 名稱或 ID，可直接指定，跳過排序猜測。**

驗證方式：以 Node Playwright（`file://` 直接開檔）逐一讀取上述 DOM 元素文字並比對 `cases_events.json`/`bird_data.json` 重新算出的 ground truth，確認一致；另外用 `setCommercialFarmStatus(1)` 模擬商業禽場破口情境，確認 Card 2、Decision Zone badge、風險分數三處連動正確；Movebank 授權流程用本地 mock `requests.get` 單元測試過 accept/retry 邏輯，並在真實 GitHub Actions 環境跑過確認 log 行為與程式碼邏輯一致。

### 尚未修復，需要人工決定或無法在此環境驗證

1. ~~**`EBIRD_API_KEY` 這個 GitHub Secret 從未設定過**~~ **（2026-09-16 已由使用者於 GitHub Secrets 補上，並經真實環境驗證修復）**：舊 log 證實 `[eBird API] 未設定 EBIRD_API_KEY 環境變數，跳過候鳥數據抓取`，`bird_data.json` 的「651 隻」是 2026-09-07 一次性手動上傳快照，從未被自動化真正抓過。使用者新增 Secret 後，最新一次真實 Actions 執行（run 35100408995 前後）確認 eBird API 抓取成功，回傳 151–158 筆新鮮的高風險觀測記錄，`bird_data.json` 的 `fetched_at_utc` 已能正常每次更新，不再凍結。
2. **`ala_bird_data.json` 從未產生過（已確認根因）**：真實環境 log 證實 `biocache.ala.org.au` 直接回傳 **HTTP 403**（不是連不上，是主動拒絕），`fetch_ala_data()` 用裸 `requests.get()`，沒有像 `smart_fetch_url()` 對 DAFF 那樣的 curl_cffi/Playwright 降級鏈。GBIF、Movebank 是正常每日更新的，真實環境已驗證 GBIF 成功寫入 488 筆記錄，不受影響。
3. **⚠️ `assets/js/purina_auth.js` 的「機密存取」密碼門完全是裝飾性的，不是真的資安控制（repo 已確認是 public）**：查過 `api.github.com/repos/bluebirdfinder/AU-H5N1-Daily-Report`，`private: false`——不是「如果公開」，是確定公開。這支檔案在前端硬編碼了明碼密碼清單，且驗證邏輯只是在頁面上蓋一層視覺遮罩（overlay），**底層 DOM 內容從頭到尾都完整存在，沒有被移除或加密**——稽核時用 Playwright 直接讀 DOM 就拿到全部風險評估數字，完全不需要通過這個「密碼驗證」；密碼本身也進了 git 歷史，就算之後改掉，舊 commit 仍查得到。任何人打開瀏覽器開發者工具、`view-source`、或直接 `curl` 都能看到頁面宣稱的「商業機密與未公開流行病學遙測數據」，密碼門形同虛設，而且「每月換密碼」這種做法對這個漏洞沒有實質幫助（擋的是「按驗證鈕」這個動作，不是「拿到資料」這件事）。這不是程式碼稽核要修的範圍，是商業/架構決策：要嘛不再宣稱「機密」，要嘛認真做私有網站/伺服器端驗證，使用者已知悉、留待內部討論後再處理。

**教訓**：往後任何「這個數字對不對」的問題，先用 `python3` 對 `cases_events.json` / `bird_data.json` 重新算一次 ground truth，不要只看 HTML 顯示的字。畫面好看 ≠ 數字是活的；有 `id` 也不代表真的有 JS 在寫它，要親自 grep 確認賦值那一行存在。

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
