# 澳洲 H5N1 Daily Update 網頁開發與發布 Standard Operating Procedure (SOP)

每當在本專案中進行功能增修、數據對齊或 UI 排版調整時，AI 助手與開發者必須嚴格遵守以下 **7 步驟 SOP 稽核與發布流程**：

---

### 📋 7 步驟 SOP 規範

#### Step 1: Feature Implementation (功能與數據修復)
- 在核心代碼檔中進行變更：`h5n1.py`（數據抓取與編譯引擎）、`report_template.html`（網頁結構與樣式模板）、`cases_events.json`（數據庫）。

#### Step 2: Syntax & Structure Check (語法與 HTML 標籤檢查)
- 確保 Python 語法無訛、無未補捉的 Exceptions。
- 檢查 HTML `<div...</div>` 標籤 100% 正確閉合（`diff = 0`），JavaScript 括號對齊無誤。

#### Step 3: Data Double Audit (官方權威數據雙重核對)
- **API 與官網數據稽核**：比對 DAFF 官方最新文字/表格數據、各州 DPIRD/PIRSA 官網數據與本機 JSON 檔案。
- **視覺數據稽核**：核對圖表 (Donut Chart)、圖例 Grid、物種風險卡片與明細表格，確保各區塊間數字 **100% 絕對完全一致**（如燕鷗 189起, 銀鷗 31起）。

#### Step 4: Mobile RWD & Modal Readability Self-Audit (手機排版與彈窗審計) 📱
- **實機 Viewport 驗證 (375px~430px)**：使用 Playwright 模擬手機螢幕載入畫面。
- **頂部 Header 週報控制列驗證**：
  - 驗證 `📺 16:9 週報簡報 (Slides)` 與 `📂 歷次週報歸檔` 按鈕在手機版與桌面版無疊字、無溢出。
  - 驗證點擊 `📂 歷次週報歸檔` 後，Modal 彈窗能順暢展開、背景半透明 Blur 遮罩運作正常，且點擊連結可開起對應週報簡報。

#### Step 5: Engine Compilation & Output Build (引擎自動編譯與簡報歸檔)
- 執行 `python h5n1.py` 重新生成 `index.html`、`live_page.html` 與 `live_page_utf8.html`，並確認控制台輸出 `網頁自動編譯成功！` 與 `[週報自動歸檔]`。
- 驗證 `h5n1_weekly_slides.html` 16:9 Web 簡報網頁佈局、Chart.js 每週趨勢圖表及 Gemini AIGrounding 新聞情報無異常。

#### Step 6: Documentation Sync (版本與文檔同步)
- 更新 `README.md` 中的數據結算起數、物種對齊說明、Gemini AI 整合與版本歷史記錄 (v2.5.2)。
- 同步更新 `CHANGELOG.md` 紀錄版本變更與修復細節。
- 更新 `task.md` 與 `walkthrough.md` 記錄最新稽核完成項目。

#### Step 7: Handover & Git Push File Checklist (檔案更新整理與推送清單) 🚀
- 整理所有變更檔案明細表，明確劃分「**哪些檔案必須 Git Push 推送至 GitHub**」。
- 提供標準 pre-formatted 的 Git commit 與 `git push` 指令，便於直接複製發布。
