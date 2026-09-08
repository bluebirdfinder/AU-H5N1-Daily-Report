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


