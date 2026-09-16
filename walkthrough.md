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


