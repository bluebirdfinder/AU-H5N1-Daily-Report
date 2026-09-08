# H5N1 全澳政策雷達、雪梨北灘突破與瀕危物種數據更新 (v2.9.0)

已成功完成 **全澳防疫政策與都會生物安全雷達 (Policy Radar Module)**、**雪梨北灘 (Warriewood) 與科夫斯港瀕危赫頓鸌案例更新**、**NSW 確診事件激增至 22 起對齊**、**物種生態庫擴充 (赫頓鸌 & 野生紅狐)**、**雙語一鍵快篩升級** 與 **全專案文檔同步 (README / CHANGELOG / SOP / Best Practices / Task)**！

---

## 🌟 最新完成重點 (v2.9.0 - 2026-09-08)

1. **🚨 NSW 確診激增至 22 起 · 攻入雪梨都會圈與瀕危物種更新 (`cases_events.json` & `h5n1.py`)**
   - **雪梨北灘 Warriewood**：`-33.6875, 151.3069`（大鳳頭燕鷗，雪梨大都會區首宗確診）。
   - **肯布拉港 Port Kembla**：`-34.4811, 150.9067`（大鳳頭燕鷗）。
   - **科夫斯港 Coffs Harbour**：`-30.2963, 153.1141`（赫頓鸌 / 雪兒水鳥，新州首例受脅瀕危留鳥）。
   - **肖爾黑文 Shoalhaven**：`-34.8833, 150.6000`（第 3 起海鳥群聚）。
   - 全澳累計確診事件升至 **484 起** (SA 271, VIC 150, TAS 29, NSW 22, WA 10, QLD 2)，商業家禽與蛋場維持 100% 零感染。

2. **🛡️ 全澳防疫政策、疫苗試驗與都會生物安全應變雷達 (Policy Radar Module)**
   - 於中英文主頁 (`index.html` & `index_en.html`) 嵌入 4 欄式政策看板：
     1. **各州圈養令對比**：維州 (VIC) 強制室內禁閉令延長 28 天至 2026/09/18；新州 (NSW) 維持自願彈性建議。
     2. **都會紅狐染疫警戒 (Urban Rethink)**：阿德萊德都市紅狐染疫引發都會防線升級（垃圾桶鎖緊、廚餘管理、防範接觸後院兔寵/犬貓）。
     3. **Taronga Zoo 疫苗臨床試驗**：雪梨塔隆加動物園針對受脅鳥類啟動 H5 疫苗試驗以收集免疫數據。
     4. **BioResponse NSW 前線 App**：新州強制全體野外巡查員安裝專用應變 App，提供 24hr 動物疾病緊急專線 (`1800 675 888`)。

3. **🦅 生態庫擴充與一鍵快篩強化**
   - 物種生態檔案擴充「赫頓鸌 (Hutton's Shearwater)」與「野生紅狐 (Red Fox)」。
   - 病例明細表新增「🚨 新州 / 雪梨北灘 (NSW 22起)」與「🌊 赫頓鸌 / 瀕危留鳥 (科夫斯港)」一鍵快篩按鈕。

4. **⚖️ 定量風險模型同步 (`risk_assessment.html` & `risk_assessment_en.html`)**
   - NSW 野生動物事件指標同步更新至 **22 起**。
   - 重申 Blayney 廠地緣評估：突破點皆為太平洋沿岸海灘，與內陸 Blayney 廠直線距離 >200km 且有藍山天然地形屏障，商業原料供應鏈維持安全。

---

## 🚀 手動 Git Upload 上傳指令清單

請複製以下 Terminal 指令進行專案 Git 提交與推送：

```bash
git add README.md CHANGELOG.md GOVT_SCRAPING_BEST_PRACTICES.md SOP.md task.md walkthrough.md report_template.html report_template_en.html index.html index_en.html live_page.html live_page_en.html live_page_utf8.html risk_assessment.html risk_assessment_en.html cases_events.json h5n1.py
git commit -m "feat(policy-radar): add National Policy Radar & Sydney metro breach (NSW 22 cases) data and sync documentation for v2.9.0 release"
git push origin main
```

