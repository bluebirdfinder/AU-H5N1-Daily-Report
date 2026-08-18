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

#### Step 4: Mobile RWD & Readability Self-Audit (手機排版與易閱讀性審計) 📱
- **實機 Viewport 驗證 (375px~430px)**：使用 Playwright 模擬手機螢幕載入畫面。
- **手機排版與觸控友善度**：
  - 頂部 sticky Header 採用彈性高 (`sticky top-0 z-50` 兩行/單行自適應)，解決長橫幅折行後壓住 Header 之問題。
  - 地圖容器 `.map-container` 新增媒體查詢（手機版 340px / 桌面版 500px），保留上下滾動空隙，避免手機大拇指滑動頁面時誤觸地圖。
  - 控制與快篩按鈕群組設置 `w-full` 與 `flex-1` 滿寬填滿、微調 Padding 與字級 (`text-[11px] px-2.5 py-1.5`)，確保單手觸控精準。
- **視覺防遮蔽與易閱讀性**：
  - 物種卡片標題區套用 `flex-wrap` 與 `shrink-0 whitespace-nowrap`，杜絕文字剪裁、疊字或 Badge 遮蔽。
  - 表格設定 `min-w-[680px]` 配合 `overflow-x-auto` 橫向滑動，避免手機端欄位文字過度擠壓。
  - 參考文獻 URL 套用 `break-all` 強制長網址自然折行，杜絕手機版 X 軸爆開白邊。
- **0 Errors 檢測**：確保 Playwright / 瀏覽器 Console 達 **0 Console Errors / 0 Warnings**。

#### Step 5: Engine Compilation & Output Build (引擎自動編譯)
- 執行 `python h5n1.py` 重新生成 `index.html`、`live_page.html` 與 `live_page_utf8.html`，並確認控制台輸出 `網頁自動編譯成功！`。

#### Step 6: Documentation Sync (版本與文檔同步)
- 更新 `README.md` 中的數據結算起數與物種對齊說明。
- 更新 `task.md` 記錄最新 Self-Audit 完成項目與修改邏輯。

#### Step 7: Handover & Git Push File Checklist (檔案更新整理與推送清單) 🚀
- 整理所有變更檔案明細表，明確劃分「**哪些檔案必須 Git Push 推送至 GitHub**」。
- 提供標準 pre-formatted 的 Git commit 與 `git push` 指令，便於直接複製發布。
