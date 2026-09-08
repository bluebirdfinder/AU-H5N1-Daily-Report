# H5N1 全澳政策雷達、雪梨北灘突破、資安白名單 CDN 與風險簡報上線 (v2.9.1)

已成功完成 **企業資安白名單 CDN 全面替換 (移除 jsDelivr/unpkg 杜絕 IT 警示)**、**風險評估模擬器預設值校正 (9月登陸 70分 / NSW 22起 35分 / 總分 37分)**、**16:9 雙語風險評估簡報 (risk_assessment_slides.html / _en.html)**、**全澳政策雷達看板**、**雪梨北灘 (Warriewood) 案例更新** 與 **全專案文檔同步 (README / CHANGELOG / SOP / Best Practices / Task)**！

---

## 🌟 最新完成重點 (v2.9.1 - 2026-09-08)

1. **🛡️ 企業資安白名單 CDN 全面替換 (Enterprise Whitelist CDN)**
   - 全面將 `Chart.js` 與 `Leaflet` 圖資庫切換為 **Cloudflare Enterprise CDN (`cdnjs.cloudflare.com`)**。
   - 徹底杜絕雀巢企業內網與 Windows Defender / IT 管理員彈出 `cdn.jsdelivr.net` / `unpkg.com` 之阻擋提示。

2. **⚖️ 定量風險模型現況校正 (`risk_assessment.html` & `risk_assessment_en.html`)**
   - 下拉選單預設對齊當前現況：**9 月（200萬隻候鳥登陸，得分 70）**、**NSW 22 起野鳥確診（得分 35）**。
   - 雷達圖多維度初始分數對齊為 `[20, 70, 30, 35, 35]`，綜合評分為 **37 分 (🟡 中風險緩衝)**。
   - 重設模擬器 (`resetSimulator()`) 邏輯精準還原為當前現況。

3. **📺 16:9 雙語風險評估簡報 (`risk_assessment_slides.html` & `risk_assessment_slides_en.html`)**
   - 正式納入 GitHub Actions 部署與每週一自動歸檔隊列。

4. **🚨 NSW 確診激增至 22 起 · 攻入雪梨都會圈與瀕危物種更新 (`cases_events.json` & `h5n1.py`)**
   - **雪梨北灘 Warriewood**：`-33.6875, 151.3069`（大鳳頭燕鷗，雪梨大都會區首宗確診）。
   - **肯布拉港 Port Kembla**：`-34.4811, 150.9067`（大鳳頭燕鷗）。
   - **科夫斯港 Coffs Harbour**：`-30.2963, 153.1141`（赫頓鸌 / 雪兒水鳥，新州首例受脅瀕危留鳥）。
   - **肖爾黑文 Shoalhaven**：`-34.8833, 150.6000`（第 3 起海鳥群聚）。
   - 全澳累計確診事件升至 **484 起** (SA 271, VIC 150, TAS 29, NSW 22, WA 10, QLD 2)，商業家禽與蛋場維持 100% 零感染。

---

## 🚀 Git 提交與推送指令清單 (Complete Push Command)

請複製以下 Terminal 指令即可一次性將所有更新與新檔案推送至 GitHub：

```bash
git add -A
git commit -m "feat(v2.9.1): enterprise cdn whitelist compliance, risk assessment slides release, nsw 22 cases sync and docs update"
git push origin main
```

