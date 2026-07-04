# 任務追蹤：澳洲 H5N1 疫情地圖自動更新系統 (已完成)

## 待辦事項
- `[x]` 建立新專案 `AU_H5N1_Daily_Update`
  - `[x]` 建立專案資料夾與 workflows 目錄
  - `[x]` 寫入 `h5n1.py`
  - `[x]` 寫入 `report_template.html`
  - `[x]` 寫入 `.github/workflows/auto_update.yml`
  - `[x]` 建立 `README.md` 說明文件
- `[x]` 執行本地編譯與驗證
  - `[x]` 執行 `python h5n1.py` 生成 `index.html`
  - `[x]` 驗證新專案 `index.html` 是否正常
- `[x]` 升級全自動地理定位與 NSW DPIRD 官網監控
  - `[x]` 整合 `https://www.dpird.nsw.gov.au/dpi/biosecurity/animal-biosecurity/avian-influenza`
  - `[x]` 導入 OpenStreetMap Nominatim 地理編碼 API
  - `[x]` 實作動態地點提取與防重覆演算法
  - `[x]` 更新 `README.md` 及專案開發日誌 `walkthrough.md`
