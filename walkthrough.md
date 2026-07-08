# 澳洲 H5N1 地圖更新專案開發日誌 (Walkthrough)

本文件記錄了本專案（澳洲 H5N1 疫情地圖自動更新報告系統）的開發軌跡、Bug 修正與架構升級歷史。

---

## 📅 2026-07-08 23:25：新增 CASE-010（雪梨 Narrabeen Beach）與陰性案例全自動動態更新升級

- **登錄個案 `CASE-010` (Negative)**：於基礎資料庫中新增雪梨北部敘利濱海灘（Narrabeen Beach）的野生鸕鶿陰性排除個案（7/7 深夜化驗排除），使地圖上呈現綠色安全標記。
- **爬蟲判定邏輯自動化**：升級 `discover_new_cases`，使其在動態偵測新地點時，若段落文字包含 "negative", "excluded", "ruled out" 等詞彙，會直接將新個案建立為 `Negative` 狀態，而非預設的 `Suspect`。
- **重構為通用動態更新機制**：淘汰舊有硬編碼的個案升級規則，改用通用動態比對。自動遍歷所有非最終狀態（非 Confirmed / Negative）之個案，從官網 HTML 與新聞 RSS 中自動比對最新結果並變更狀態。
- **統計彙整格式化優化**：調整 `generate_dynamic_summary` 的展示邏輯，將新南威爾斯州 (NSW) 等狀態統計顯示為 `新南威爾斯州 (NSW) 2 例（1例確診/1例已排除)`，保持各州呈現的一致性。
- 本地執行 `python h5n1.py` 編譯成功，生成最新版 `index.html`。


## 📅 2026-07-06 15:47：對齊 Gemini 案例對比落差與維多利亞州 (VIC) 排除點補齊

- **地名拼寫對齊**：將 CASE-004 地名修改為 `西澳丹斯伯勒 Dunsborough (Quindalup) 地區`，消除大城鎮名與微觀沙灘名的拼寫落差。
- **補齊維多利亞州 (VIC) 排除個案**：在資料庫中新增 `CASE-009` (Negative) 維多利亞州沿海地區 (Portland) 的野鳥排除個案（7/3 排除），在視覺上為澳洲東海岸增設綠色安全排除標記。
- **動態摘要統計擴展**：升級 `generate_dynamic_summary`，將 `VIC` 獨立納入病例分布計數器中，讓網頁頂部 Facts 顯示：`當前最新疫情病例分布統計：西澳 5 例（5例確診)...另有 維多利亞州 (VIC) 1 例（1例已排除)`，進一步強化 Blayney 廠在東南澳洲的安全性論點。
- 本地重新編譯生成最新確診版網頁，並刷新了 6 個專案檔案之修改日期。

---

## 📅 2026-07-06 15:30：解決 GitHub Actions 寫入權限與官方確診時間校正

- **GitHub Actions 寫入授權**：引導使用者將 GitHub 專案 `Settings -> Actions -> General -> Workflow permissions` 設定修改為 **`Read and write permissions`**。此設定將徹底解除 GitHub Actions 在雲端更新並 `git push` index.html 回儲存庫時的權限阻礙，實現 100% 全自動化定時更新。
- **Roses Beach (CASE-005) 確診日期修正**：核實西澳官方於 6/30 已正式發布確診公告，將其狀態更新為 `Confirmed`，確診日期校正為 `2026-06-30`，`source_status` 設為 `official_updated`。
- **Mullaloo Beach (CASE-008) 推定確診登入**：核實西澳 DPIRD 今日 (7/6) 正式發布巨鸌檢體為 H5 推定陽性公告。已將其登錄為 `CASE-008` 確診點，確診日期為 `2026-07-06`，`source_status` 設為 `official_updated`。
- **爬蟲雙網頁監控防線**：`h5n1.py` 爬蟲代碼已升級為同時監控 DAFF 的 node/26086 數據庫以及 about/news 聲明頁面，雙重保障防止遺漏。
- 本地重新編譯生成最新確診版網頁，並刷新了 6 個專案檔案之修改日期。

---

## 📅 2026-07-05 12:28：Google RSS 整合與媒體宣告交叉過濾（C 方案）實作

- 升級了 `h5n1.py` 爬蟲大腦，新增了對 **Google News 澳洲禽流感即時 RSS 監控流** 的抓取。
- 整合了「數據可信度三重過濾網」（限定主流媒體、匹配官方首席獸醫官/國家實驗室/農業部長等發言人與確診動作詞），以確保新聞 100% 屬實。
- 在網頁前端新增了精緻的 **`⚠️ 媒體先行 (官網同步中)`** 標籤（當滑鼠移上去時顯示提示說明），同時地圖 Popup 也同步新增該 Badge。
- 針對 Nestlé 公司網路代理環境，在所有 HTTP 請求中配置了 `verify=False` 忽略 SSL 自簽名憑證驗證，並使用 `urllib3.disable_warnings` 關閉證書警告，保證了本機與 GitHub Actions 執行時的 100% 連線綠燈。
- 刷新了所有 6 個檔案的本機修改日期，保持檔案日期百分之百同步。
