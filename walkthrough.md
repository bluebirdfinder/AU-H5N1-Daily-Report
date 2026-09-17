# Claude Code 全專案架構稽核與資料完整性修復 (v2.10.0, 2026-09-16)

這是本專案第一次交給 Claude Code 完整稽核（先前版本由 Antigravity 開發，未經 Claude 審閱）。稽核方法：逐區塊比對 `index.html`/`risk_assessment.html` 兩個頁面的功能區塊，記錄每個區塊的資料來源（動態模板變數／JS 讀 embedded JSON／純靜態寫死文字），再用 Python 重算 `cases_events.json`/`bird_data.json` 的 ground truth 與頁面實際顯示比對，找出落差。

## 發現與修復摘要

1. **NSW/SA/VIC/TAS 事件數凍結問題**：`risk_assessment.html` 顯示 NSW 22 起，但資料庫實際已達 32 起（SA/VIC/TAS 同樣過期）。根因是 `h5n1.py` 的 `parse_daff_official_stats()` 離線 fallback 用寫死字典，而非呼叫既有卻從未被呼叫過的 `compute_stats_from_cases()`；`risk_assessment.html` 也從未真正讀過任何活資料（`window.casesEventsEmbedded` 是死綁定，全 repo 沒有任何腳本賦值它）。修復後兩個問題都解決，並用 Playwright 實測驗證顯示的數字與資料庫一致。
2. **候鳥數量停滯 651 隻問題**：`bird_data.json` 本身確實 12 天沒更新（疑似 `EBIRD_API_KEY` 失效或未設定，需人工確認），但更關鍵的是：即使資料有更新，前端多處讀取一個不存在的欄位 `state_summary.NSW.total_birds`，永遠 fallback 到寫死數字；首頁候鳥總數大字完全沒有 JS 綁定。兩者都已修復，並新增資料過期時的視覺警示。
3. **Playwright 實測意外發現**：`risk_assessment.html` 的初始化鏈一旦有任何一步拋出例外（測試時是 Chart.js CDN 被沙盒環境的防火牆擋下），後續所有步驟（含算風險分數的 `recalculateRisk()`）會整串不執行——這是本專案自己在 README 反覆提到「企業防火牆擋 CDN」痛點的具體體現。已改為逐步獨立 try/catch。
4. **同頁自相矛盾**：不比對外部資料也能發現的問題，例如同一份 `risk_assessment.html` 裡「全澳事件數」一處寫 498、另一處寫 484；風險分數量表顯示 37，決策矩陣卡片卻寫「當前現況: 28」。已改為單一資料來源動態產生，不會再分裂。
5. **資安提醒（未修復，留待人工決定）**：`purina_auth.js` 的「內部機密」密碼門是純前端裝飾——明碼密碼寫在 JS 裡，且驗證邏輯只蓋一層視覺遮罩，底層 DOM 資料完整存在，用瀏覽器開發者工具或 Playwright 都能繞過取得全部資料。

## 新增的專案記憶

- `CLAUDE.md`：核心規則 + 已知資料完整性陷阱清單。
- `.claude/skills/h5n1-data-audit/SKILL.md`：核對頁面數字/候鳥資料的標準稽核流程。

---

# 二次修復：EBIRD_API_KEY 補設、Gemini 模型再度全滅、Movebank 真實串接 (v2.10.1, 2026-09-16)

v2.10.0 稽核完成後，使用者實際操作 GitHub Secrets 與追問時，又浮現三個需要在真實環境反覆驗證才能確認的問題：

1. **`EBIRD_API_KEY` 確認補設成功**：使用者於 GitHub Settings → Secrets 新增後，觸發真實 workflow 執行，log 證實 eBird API 成功抓到 151–158 筆新鮮觀測，`bird_data.json` 恢復正常更新頻率。
2. **Gemini 備援模型清單「修好又壞」**：v2.10.0 換上的 `gemini-2.5-flash-lite`/`gemini-2.5-pro` 在同一天 2 小時後的真實測試中也雙雙 404「no longer available to new users」——這證明具名備援模型清單本身是脆弱策略（Google 下架速度可以快於一次稽核週期）。最終改為放棄猜測新模型名稱，直接讓唯一持續驗證有效的 `gemini-2.5-flash` 重試一次。
3. **Movebank 候鳥走廊資料是假的**：使用者追問「候鳥數據還有哪個抓不到」時發現，`fetch_movebank_data()` 從頭到尾沒有呼叫過任何 Movebank API，只是依環境變數印狀態訊息、永遠輸出寫死的 6 條示範航跡（日期凍結在 8 月）。使用者確認持有真實帳密後，改為呼叫新函式 `fetch_movebank_live_tracks()`：以「澳洲關鍵字 > 南半球緯度 > 物種關鍵字 > 下載權限」排序候選研究，並實作 Movebank 官方的授權條款自動同意（`license-md5`）協議。真實環境驗證授權流程本身正常（多筆 study 成功通過驗證），但排到的候選研究近 30 天內都沒有個體回傳 GPS 座標，判斷是已結束的歷史研究，系統誠實標示 `is_live_data:false` 並安全退回範例資料，不偽裝即時連線。

**教訓**：候選函式「有沒有真的打 API」不能只看有沒有 try/except 或有沒有印訊息，要親自 grep 函式體內是否真的有 `requests.get`/`requests.post` 呼叫外部網址；「看起來像是有容錯機制」跟「其實從未真正嘗試過」是兩件事，後者往往比真正失敗更難發現，因為錯誤訊息看起來完全正常。

---

# 三次修復：全 repo 稽核死角、ALA 降級鏈、Movebank 排序、候鳥物種清單 (v2.10.2, 2026-09-17)

使用者問了一個看似簡單卻直接戳破前兩輪稽核盲點的問題：「整個專案裡的所有網頁和程式架構，你全部都稽核完了嗎？」

1. **三份週報簡報從未被稽核**：逐一清點 repo 才發現根目錄有 13 個 HTML 檔案，不只 2 個。`h5n1_weekly_slides.html`（疫情週報）與 `risk_assessment_slides.html`/`_en.html`（風險評估模型週報）完全獨立於主頁面，`sync_weekly_slides()`/`sync_risk_assessment_weekly()` 每週一自動跑，但只做「歸檔」跟「換封面日期」，內容數字完全沒被前兩輪任何一次修復觸及——跟主頁面修過的死綁定是同一類問題，只是這次連綁定的嘗試都沒有。已接上 `cases_events.js`，並用 Playwright 對全部 8 個頁面重新驗證跨頁一致性，確認無矛盾。
2. **ALA 403 修復途中意外揪出更底層的 bug**：`fetch_ala_data()` 改用 `smart_fetch_url()` 四段降級鏈後，發現 `playwright_fetch_url()` 在一般網址導航情境下（未傳入 `html_content`）永遠 `return html_content`——也就是永遠回傳呼叫時傳入的 `None`，而不是它自己抓到、存在 `fetched_html` 變數裡的真實內容。這代表這條「真實瀏覽器」防線，包括原本 DAFF 也在用的那條，一直以來對「導航到目標網址」這種一般用法都是死的。修復後真實環境證實對 DAFF 等既有用途確實更穩，但 ALA 網站本身仍會擋 GitHub Actions 的來源 IP，即使换用真的無頭瀏覽器也一樣被擋（回應只有 195 字元，遠低於可信門檻）。
3. **Movebank 排序演算法的真實 bug，由使用者親自用 Movebank 官網搜尋揪出來**：使用者直接在 Movebank 上用 taxon search 找到 3 個真正相關的 EAAF 候鳥研究（Tracking Curlew sandpipers/Great Knots/Red-necked stints along the EAAF），名稱完全沒有「Australia」字樣。真實環境 log 證實：前一輪排序邏輯給「名稱含 Australia」+100 分、物種關鍵字只給 +10 分，導致 Water buffalo、Swamp wallabies 這類跟候鳥完全無關但名稱含 Australia 的研究排到前面。重新調整權重後，這 3 個研究確實排到最高分，還額外挖出好幾個同樣相關的研究——但全部卡在 Movebank 官方「需另外向擁有者申請下載權限」，這步無法自動化。
4. **候鳥物種清單擴充中的方法論教訓**：使用者提供 Wildlife Health Australia 與 DCCEEW/BirdLife Australia 兩份官方文件全文（因為這幾個網域被此環境的網路政策擋掉，WebFetch 全部失敗，只能靠使用者手動貼上）。過程中發現一個容易誤踩的陷阱：DCCEEW/BirdLife 的「國家風險評估」分數 = 易感性 + 脆弱性（滅絕風險）相加，不能直接當「監測用高風險物種清單」使用——原文自己警告劍尾鸚鵡、平原走鴴等極危陸鳥雖列高風險，實際「不太可能暴露於病毒或傳播病毒」。最終只採用文中明確點名「易感性高、會傳播病毒」的物種（黑天鵝、麥雞鵝、尖尾濱鷸），刻意排除純脆弱性驅動、跟本專案監測地理範圍無關的離島特有種。

**教訓**：「全部稽核完了嗎」這種問題不能只靠記憶回答，要真的去 `find`/`ls` 整個 repo 清點檔案清單，因為前兩輪的稽核範圍本身就是根據使用者最初提到的兩個頁面設定的，範圍設定錯了，再怎麼稽核也不會發現範圍外的問題；另外，拿權威來源擴充清單時，要先確認這份來源實際回答的是什麼問題，同一份報告的高分排名可能來自完全不同、甚至互斥的評分邏輯。

---

# 四次修復：本機環境重建、ALA 前端防禦性綁定、Movebank 二次驗證與靜默失敗診斷 (v2.10.3, 2026-09-17)

使用者把整個 repo 下載到本機 Windows 資料夾繼續工作，並接續上一輪留下的三個「等你決定」事項，指定先做 ALA 前端顯示與 Movebank 排序驗證，密碼門留到最後。

1. **本機資料夾不是 git repo，既有稽核方法失效**：下載下來的資料夾沒有 `.git`，代表 `git diff`/`git log` 這套本專案反覆依賴的稽核方法完全用不了。補上 `git init`、接上 `origin`（`bluebirdfinder/AU-H5N1-Daily-Report`）、`git fetch`，並用 `git reset origin/main`（只動索引、不覆寫既有下載檔案）讓本機 `main` 分支追蹤 `origin/main`，確認本機檔案與遠端最新 commit 只差抓取時間戳記，沒有真實資料落差。
2. **ALA 前端顯示：抓取端仍是死的，改做防禦性綁定而非模仿 GBIF 整塊複製**：先用 `gh run view` 拉真實 GitHub Actions log 確認 `fetch_ala_data()` 目前依然每次失敗——`biocache.ala.org.au` 對 GitHub Actions 來源 IP 只回傳 195 字元內容，跟 v2.10.2 記錄的現象一致，是 IP 層級封鎖，本輪沒有再花時間嘗試繞過。既然資料源仍不可達，直接照抄 GBIF 那樣做一整塊新的資料源展示區沒有意義；改為讓 `fetch_ala_data()` 不論成功失敗都寫出 `ala_bird_data.json`/`assets/js/ala_bird_data.js`（失敗時是 `available:false` 的空殼），並在 `risk_assessment.html`/`_en.html` 加上讀取這個檔案的 `renderAlaOnMap()` 地圖圖層——資料一旦哪天能抓到就會自動顯示，抓不到時安全跳過，不會讓 `<script>` 標籤在正式環境 404、也不會顯示假的「0 筆」狀態。用本機 `python -m http.server` 開真實頁面測試才發現：這個瀏覽工具對 `file://` 只給靜態快照、不會真的跑 JS，改用 HTTP server 才能驗證中英文兩版都正確載入且 console 無錯誤。
3. **Movebank 排序修正得到真實環境直接證實**：拉當天稍早（00:19）的真實 log，確認上一輪修正的排序權重確實把使用者驗證過的 3 個 EAAF 研究排到最前面（`Tracking Curlew sandpipers along the EAAF` 以 1100 分排名第一）——排序邏輯本身修對了，只是這些研究在 Movebank 端目前沒有可下載的新座標，系統照設計安全退回範例資料。
4. **意外抓到一個新的靜默失敗**：同一天再晚 40 分鐘的下一次執行，Movebank 回報「全站共 0 個 study」，跟稍早的 8769 個天差地遠，但程式碼在這種「請求技術上成功、解析出 0 筆」的情況完全沒印任何診斷，事後無法判斷原因。補上一行診斷（印出原始回應長度與前 200 字），下次再發生才有線索可查，而不是又要重新從頭猜測。

**教訓**：使用者只是說「我把檔案抓到本機資料夾」，不代表這個資料夾有 `.git`——往後遇到類似描述，第一步先確認 git 狀態，不要預設既有的稽核工具鏈能直接沿用。另外，修完程式碼只要有跑過 `python h5n1.py`（哪怕只是為了驗證語法），跑完一定要立刻檢查 `git status`，把沙盒離線環境產生的降級資料用 `git restore` 復原，只留下真正手動修改的檔案，避免工作目錄裡混著沙盒資料誤導下一次判斷。

---

# H5N1 風控核心準則確立、候鳥雙軌數據重構、16:9 簡報與地圖一體化升級 (v2.9.5)

已成功完成 **確立 NSW 商業禽舍「零感染 (Area Freedom)」為唯一生死防線**、**候鳥雙軌數據（模型推估 vs 現場實測）架構重構**、**2 年推演時間軸數據解耦與 DAFF 498 起事件對齊**、**16:9 簡報 Slide 4 候鳥數據補齊與全地圖左側一體化極簡面板 (Zero East-Coast Obstruction)**、**RWD 換頁按鈕溢出修復** 與 **全專案文檔同步 (README / CHANGELOG / SOP / Task / Walkthrough)**！

---

## 🌟 最新完成重點 (v2.9.5 - 2026-09-08)

1. **🚨 確立最高指導原則：NSW 商業家禽場「零感染 (Area Freedom)」為唯一生死防線 (`AGENTS.md` / `AGENT.md`)**
   - 確立台灣檢疫法規以 NSW 全轄區為宣告單位，嚴禁以距離 Blayney 工廠公里數模糊焦點。
   - 風險評估全面聚焦於「逼近 NSW 州界之動態」與「NSW 野鳥外溢至商業家禽場之風險」。

2. **🦅 雙軌候鳥數據架構（推估總數 vs 現場實測總數）與 4 大候鳥源判讀指南**
   - 清楚分離「📊 歷史季節模型【推估總數】(~50 萬隻先鋒 / NSW: ~6 萬隻)」與「🦅 現場實測【實際總數】(1,407 隻去重實測 / NSW: 286 隻)」。
   - 全專案 HTML 嵌入 `💡 4 大候鳥數據源判讀指南` 互動式 Modal 彈窗。

3. **📊 2 年推演時間軸圖表重構（確診案件與候鳥數據全面解耦）**
   - 確診案件即時對齊 DAFF 官方 498 起（NSW 22 起），推演曲線自 2026.10 起順暢銜接至 2028.06。
   - 候鳥數據分離「實地觀測統計 (18 萬隻)」與「季節模型推估 (50 萬隻先鋒至 220 萬隻峰值)」。

4. **📺 16:9 簡報 Slide 4 候鳥數據補齊與全地圖「左側一體化極簡面板 (All-on-Left Compact HUD & Legend)」**
   - Slide 4 頂部補齊 4 欄式生態 HUD 數據條；地圖浮動視窗與圖例整合至左上角（195px），徹底釋放 NSW、VIC、TAS、珊瑚海與塔斯曼海航線視野（100% 乾淨無遮擋）。
   - 修復 1366×768 筆電解析度下底部換頁按鈕溢出問題，全螢幕與多解析度自適應常駐顯示。

5. **🌐 風險評估主網頁地圖同步升級**
   - `risk_assessment.html` 與 `risk_assessment_en.html` 同步升級為左側一體化風控 HUD 與圖例面板。

---

## 🚀 Git 提交與推送指令清單 (Complete Push Command)

請複製以下 Terminal 指令即可一次性將所有更新與新檔案推送至 GitHub：

```bash
git add -A
git commit -m "feat(v2.9.5): nsw zero-cases core principle, dual-track migratory metrics, timeline decoupling, slide4 left-panel hud and full doc sync"
git push origin main
```


