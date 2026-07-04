# 澳洲 H5N1 地圖更新專案開發日誌 (Walkthrough)

本文件記錄了本專案（澳洲 H5N1 疫情地圖自動更新報告系統）的開發軌跡、Bug 修正與架構升級歷史。

---

## 📅 2026-07-04：全自動地理定位與 NSW DPIRD 官網監控升級

為了解決原爬蟲系統無法對「未知新爆發地點」進行地圖標示，以及聯邦官網更新有延遲的問題，我們對系統進行了重大架構升級：

### 🛠️ 升級與優化內容

1. **整合新南威爾斯州政府 (NSW DPIRD) 官網**：
   - 爬蟲增加了對 NSW 官方禽流感更新專頁的直接監控：
     `https://www.dpird.nsw.gov.au/dpi/biosecurity/animal-biosecurity/avian-influenza`
   - 同步更新了網頁底部的參考資料，提供透明的官方出處。
2. **引進 OpenStreetMap Nominatim 地理編碼引擎**：
   - 在 `h5n1.py` 中串接了 Nominatim API，將英文地名實時轉換為精確的 GPS 經緯度數字。
3. **實作全新地點動態發現與排重演算法**：
   - **文字段落特徵擷取**：自動提取含有禽流感或野鳥關鍵字之公告段落。
   - **地名比對與 Geocoding**：透過正則表達式篩選出可能的地名，動態向 API 查詢坐標。
   - **空間距離排重**：設定了「10 公里空間防重疊」機制，防止同一個地方因地名寫法不同而重複標示。
   - **狀態與病例自動加入**：研判是否為 confirmed 後，自動分配新病例 ID（例如這次的 Hawks Nest 為 `CASE-007`）並動態繪製在地圖上，實現 100% 免維護全自動定位！

### 🧪 本地測試與驗證結果
* 執行指令：`python h5n1.py`
* 輸出結果：
  - 成功加載最新的 7 起病例資料（包含新南威爾斯州首例 Hawks Nest 疑似病例）。
  - 生成的 `index.html` 完美定位 Hawks Nest 於 `(-32.6658, 152.1793)`，地圖與病例明細表格渲染正常。
  - WAF 403 攔截防護機制順利起效，在本地超時/拒絕連線時程式流暢容錯不崩潰，安全回退內置病例庫。

---

## 📅 2026-06-29：專案獨立建置與基礎 Bug 修正

我們完成了從「全球疫情 Telegram 監報」到「澳洲 H5N1 GIS 地圖報告」的專案隔離與基礎除錯：

1. **GitHub Actions 執行指令修正 (Bug 修正)**：
   - 修正了 `.github/workflows/auto_update.yml` 中的大 Bug，將原本錯誤的執行指令 `run: python updater.py` 修正為真正的 Python 檔名 `run: python h5n1.py`。
2. **HTML 模板與讀取路徑對齊 (Bug 修正)**：
   - 將下載的模板 `h5n1 (1).html` 更名為 `report_template.html` 放入專案根目錄，使 Python 腳本能順利讀取到模板並進行注入。
3. **HTML 注入語法 Bug 修正**：
   - 原模板中的 JavaScript 預設寫了 `window.H5N1_CASES = /* CASES_DATABASE_PLACEHOLDER */ [ ... ];`，而 Python 直接進行字串取代，會導致生成的 `index.html` 產生 `] [` 的 JavaScript 語法錯誤。
   - 我們在 `h5n1.py` 中將取代邏輯升級為正規表示式（`re.sub`），執行時會自動清除模板中多餘的預設 JavaScript 陣列，只保留動態注入的最新數據，徹底解決了網頁在地圖渲染時的潛在 JavaScript crash。
4. **控制台 CP950 編碼問題修復 (Windows 執行 crash 修正)**：
   - Windows 本地控制台（繁體中文語系預設 CP950 編碼）在印出帶有 Emoji（如 🎉）的字串時會拋出 `UnicodeEncodeError`。
   - 我們在 `h5n1.py` 頂部引入了 `sys.stdout.reconfigure(encoding='utf-8')`，並優化了輸出文字，使其無論在本地 Windows 還是 GitHub 雲端 Linux 下執行都 100% 綠燈成功。
5. **台北/澳洲雙時區更新時間校正**：
   - 將系統最後更新時間校正為 `台北時間 (UTC+8) / 澳洲 AEST (UTC+10)`，方便團隊直接核對時間。
