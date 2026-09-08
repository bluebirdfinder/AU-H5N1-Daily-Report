import json
import os
import math
import time
from playwright.sync_api import sync_playwright

def generate_nsw_map():
    cases_file = "cases_events.json"
    if not os.path.exists(cases_file):
        print(f"Error: {cases_file} not found!")
        return
        
    with open(cases_file, "r", encoding="utf-8") as f:
        all_cases = json.load(f)
        
    nsw_cases = [c for c in all_cases if "NSW" in c.get("location", "") or "新南威爾斯" in c.get("location", "")]
    print(f"Found {len(nsw_cases)} NSW cases.")

    factory_lat, factory_lng = -33.521027, 149.236425

    # Calculate distance helper
    def calculate_distance(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    # Calculate jittered coordinates so同地點個案不重疊，全部 11 個標籤皆清楚分散可見
    coord_groups = {}
    for idx, c in enumerate(nsw_cases, 1):
        key = (round(c.get("latitude"), 4), round(c.get("longitude"), 4))
        if key not in coord_groups:
            coord_groups[key] = []
        coord_groups[key].append((idx, c))

    jittered_cases = []
    for key, group in coord_groups.items():
        n = len(group)
        for g_idx, (item_idx, c) in enumerate(group):
            orig_lat = c.get("latitude")
            orig_lng = c.get("longitude")
            if n == 1:
                j_lat, j_lng = orig_lat, orig_lng
            else:
                # Radial offset for overlapping coordinates
                angle = (2 * math.pi / n) * g_idx
                radius = 0.045  # degree offset approx 4-5km for clear visual separation
                j_lat = orig_lat + radius * math.sin(angle)
                j_lng = orig_lng + radius * math.cos(angle) * 1.2
            
            dist = calculate_distance(orig_lat, orig_lng, factory_lat, factory_lng)
            jittered_cases.append({
                "index": item_idx,
                "orig_lat": orig_lat,
                "orig_lng": orig_lng,
                "lat": j_lat,
                "lng": j_lng,
                "date": c.get("found_date") or c.get("notify_date"),
                "location": c.get("location"),
                "species": c.get("species"),
                "distance": int(round(dist))
            })

    html_content = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <title>NSW H5N1 確診 11 起案例與 Nestlé Blayney 廠地理分布圖</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Leaflet CSS & JS (Cloudflare Enterprise Whitelist CDN) -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Noto+Sans+TC:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', 'Noto Sans TC', sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 16px; }}
        #nswMap {{ height: 700px; width: 100%; border-radius: 12px; border: 1.5px solid #334155; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5); }}
        
        /* 精緻小巧工廠 Icon (不遮擋地圖) */
        .small-factory-pin {{
            background: #eab308;
            color: #0f172a;
            font-size: 16px;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid #ffffff;
            box-shadow: 0 0 12px rgba(234, 179, 8, 0.9), 0 2px 6px rgba(0,0,0,0.6);
            cursor: pointer;
        }}

        /* 11 起確診事件獨立編號 Badge */
        .case-number-badge {{
            background-color: #ef4444;
            color: #ffffff;
            font-weight: 800;
            font-size: 12px;
            width: 26px;
            height: 26px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid #ffffff;
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.8);
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="max-w-7xl mx-auto space-y-4">
        <!-- 簡潔頂部資訊欄 -->
        <div class="bg-slate-800 border border-slate-700 rounded-xl p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
            <div>
                <div class="flex items-center gap-2 mb-1">
                    <span class="bg-red-600 text-white text-[11px] font-black px-2 py-0.5 rounded-full uppercase">NSW 11 起案例精確定位圖</span>
                    <span class="text-xs text-amber-400 font-mono font-bold">DAFF 24/08/2026 官方對齊</span>
                </div>
                <h1 class="text-xl font-bold text-white tracking-tight">新南威爾斯州 (NSW) 全部 11 起確診事件與 Nestlé Blayney 廠空間分布</h1>
                <p class="text-xs text-slate-300 mt-0.5">
                    註：同地點多起案例已進行微幅環狀放射分散，確保 <strong class="text-red-400">1 ~ 11 號所有個案標籤皆獨立清晰可見</strong>。
                </p>
            </div>
            <div class="flex items-center gap-4 text-xs">
                <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-amber-500 inline-block"></span> 🏭 Blayney 工廠</div>
                <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-red-500 inline-block"></span> 🔴 確診事件 (共 11 起)</div>
            </div>
        </div>

        <!-- 地圖容器 -->
        <div id="nswMap"></div>

        <!-- 11 起案例詳細對照清單 -->
        <div class="bg-slate-800 border border-slate-700 rounded-xl p-4 space-y-3">
            <h2 class="text-sm font-bold text-white flex items-center gap-2">
                <span>📌</span> NSW 11 起確診事件圖示編號對照清單
            </h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2.5 text-xs font-mono">
"""

    for c in jittered_cases:
        html_content += f"""
                <div class="bg-slate-900/80 p-2.5 rounded-lg border border-slate-700/60 flex items-center justify-between">
                    <div>
                        <span class="font-bold text-red-400">#{c['index']}</span>
                        <span class="text-slate-300 font-sans ml-1">{c['location'].split(' ')[-1]}</span>
                        <div class="text-[10px] text-amber-300 font-sans truncate">{c['species'].split(' ')[1] if ' ' in c['species'] else c['species']} ({c['date']})</div>
                    </div>
                    <span class="text-[11px] text-emerald-400 font-bold shrink-0">{c['distance']}km</span>
                </div>"""

    html_content += f"""
            </div>
        </div>
    </div>

    <script>
        const factoryLat = {factory_lat};
        const factoryLng = {factory_lng};
        const casesData = {json.dumps(jittered_cases, ensure_ascii=False)};

        const map = L.map('nswMap').setView([-34.5, 147.5], 6);

        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap'
        }}).addTo(map);

        // 小巧精緻工廠小圖案 (不遮擋地圖)
        const factoryIcon = L.divIcon({{
            className: 'custom-factory-pin',
            html: '<div class="small-factory-pin" title="Nestlé Purina Blayney 廠">🏭</div>',
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        }});

        L.marker([factoryLat, factoryLng], {{ icon: factoryIcon, zIndexOffset: 2000 }}).addTo(map)
            .bindPopup('<strong style="color:#eab308;">🏭 Nestlé Purina Blayney 廠</strong><br>GPS: -33.5332, 149.2524<br>海拔 860 米 (內陸高地)');

        // 獨立繪製全部 11 個個案標籤
        casesData.forEach(c => {{
            const markerIcon = L.divIcon({{
                className: 'custom-case-pin',
                html: `<div class="case-number-badge" title="個案 #${{c.index}}">${{c.index}}</div>`,
                iconSize: [26, 26],
                iconAnchor: [13, 13]
            }});

            L.marker([c.lat, c.lng], {{ icon: markerIcon }}).addTo(map).bindPopup(`
                <div style="color:#0f172a; font-size:12px; line-height:1.5;">
                    <strong style="color:#ef4444;">NSW EVENT #${{c.index}}</strong><br>
                    <strong>位置:</strong> ${{c.location}}<br>
                    <strong>物種:</strong> ${{c.species}}<br>
                    <strong>日期:</strong> ${{c.date}}<br>
                    <strong>距 Blayney 廠:</strong> ${{c.distance}} 公里
                </div>
            `);

            // 同地點分散引線 (若是同地點個案，畫一條極淡細線回原始座標)
            if (c.orig_lat !== c.lat || c.orig_lng !== c.lng) {{
                L.polyline([[c.orig_lat, c.orig_lng], [c.lat, c.lng]], {{
                    color: '#ef4444',
                    weight: 1,
                    opacity: 0.5
                }}).addTo(map);
            }}
        }});

        // 自動調整鏡頭包含 Blayney 工廠與全部 11 個點位
        const points = [[factoryLat, factoryLng], ...casesData.map(c => [c.lat, c.lng])];
        map.fitBounds(points, {{ padding: [40, 40] }});
    </script>
</body>
</html>
"""

    html_file = "nsw_cases_map.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    screenshot_file = "nsw_cases_map.png"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 1150})
        abs_path = os.path.abspath(html_file)
        page.goto(f"file:///{abs_path}")
        time.sleep(3.5)
        page.screenshot(path=screenshot_file, full_page=True)
        browser.close()

    print(f"Successfully generated clean map image with all 11 markers: {screenshot_file}")

if __name__ == "__main__":
    generate_nsw_map()
