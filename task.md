# 任務清單：澳洲 H5N1 疫情週報 16:9 Web 簡報與圖表修復

- [x] 建立與編排 16:9 Web 投影片 `h5n1_weekly_slides.html`
  - [x] 設計自適應 16:9 CSS 佈局系統與黑暗科技視覺風格
  - [x] 撰寫 9 頁核心投影片內容與圖表元素
  - [x] 第 8 頁改版為「全澳疫情數據摘要卡片 + 16:9 每週趨勢圖表 (Weekly Epi-Curve)」
  - [x] 實現鍵盤控制、頁碼跳轉、全螢幕 mode 與動態過場效果
- [x] 修復網頁每週趨勢圖表時間軸截斷問題 (`report_template.html` & `index.html`)
  - [x] 替換寫死的 8月W2 週次標籤，改用 `generateWeekLabels()` 動態解析至 `9月W1`
  - [x] 重新執行 `python h5n1.py` 自動生成最新 `index.html`
- [x] 驗證簡報網頁功能與畫面品質
  - [x] 使用 Playwright 進行網頁多頁截圖驗證
  - [x] 確保無過載溢出、字體與圖表排版完美
- [x] 文檔與版本歷史同步
  - [x] 更新 `README.md`（包含核心功能特點與 v2.5 版本歷史）
  - [x] 建立 `CHANGELOG.md` 紀錄 v2.5.0 變更明細
  - [x] 更新 `SOP.md` 規範簡報驗證與文檔同步流程
  - [x] 更新 `walkthrough.md` 紀錄最新實例截圖與成果
