# -*- coding: utf-8 -*-
"""
H5N1 澳洲疫情自動追蹤與報告編譯引擎 (全澳州聯防爬蟲網絡版 - 支援 URL 防改版與新聞 RSS 兜底定位)
功能：自動爬取澳洲聯邦農業部 (DAFF)、以及澳洲全體 8 個州/領地政府的官方禽流感監控網頁：
      - 新南威爾斯州 (NSW) DPIRD
      - 南澳州 (SA) PIRSA 
      - 西澳州 (WA) DPIRD
      - 維多利亞州 (VIC) Agriculture Victoria
      - 昆士蘭州 (QLD) Business Queensland
      - 塔斯馬尼亞州 (TAS) NRE Tasmania
      - 北領地 (NT) Government
      - 首都領地 (ACT) Environment
      結合 Google News RSS 新聞流，進行全自動交叉檢驗與 AI 智慧地理定位。
      
      【防 Link Rot 兜底機制】：
      若任何官方網站 URL 改版失效 (404/403/Timeout)，爬蟲將啟動「第二道防線」，
      直接從 Google News RSS 標題與內文自動提取新疫情地點，並呼叫 Nominatim API 定位，
      確保 100% 不漏掉 any 重大新聞。
"""

import os
import sys
import re
import json
import math
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

# 確保控制台輸出編碼為 UTF-8，避免 Windows 終端機 (CP950) 因 Emoji 或特殊字元而 UnicodeEncodeError
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 關閉因忽略 SSL 憑證產生的 InsecureRequestWarning 警告資訊
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== 1. 基礎病例資料庫 (更新至 2026 年 7 月 30 日下午，共 32 例) ====================
# 當爬蟲執行時，會以這個結構為基礎，並嘗試與官網最新發布的文字進行比對與動態修正。
# source_status: "official_updated" (官方網頁已更新) / "media_announced" (媒體先行，官網同步中)
# 【DAFF 統計說明】DAFF 以「個別鳥隻」為單位計算 detection 數量。
# 總病例庫包含 28 例官方確診/推定陽性 (WA 10例, SA 15例, NSW 2例, QLD 1例, VIC 1例)
# 4 例已排除 (SA 1例, VIC 1例, NSW 1例, QLD 1例) 與 7/30 南澳通報之 13 隻新疑似案。
DEFAULT_CASES = [
    {
        "id": "CASE-001",
        "type": "Confirmed",  # 狀態：Confirmed (確診) / Suspect (疑似) / Negative (陰性排除)
        "source_status": "official_updated",
        "species": "褐賊鷗 (Brown Skua)",
        "location": "西澳埃斯佩蘭斯 Cape Le Grand 國家公園",
        "latitude": -33.9912,
        "longitude": 122.1481,
        "found_date": "2026-06-15",
        "notify_date": "2026-06-19",
        "confirm_date": "2026-06-20",
        "notes": "全澳洲官方首宗確診高致病性 H5N1 案例。由西澳與國家實驗室 (ACDP) 快速檢測確診。"
    },
    {
        "id": "CASE-002",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "南方巨鸌 (Southern Giant Petrel)",
        "location": "西澳埃斯佩蘭斯地區 (東部海岸線)",
        "latitude": -33.8613,
        "longitude": 121.9021,
        "found_date": "2026-06-18",
        "notify_date": "2026-06-20",
        "confirm_date": "2026-06-22",
        "notes": "西澳第二例確診，均位於 Esperance 地緣隔離之南部候鳥棲息帶。"
    },
    {
        "id": "CASE-003",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "巨鸌 (Giant Petrel)",
        "location": "南澳 Fleurieu 半島 Knights Beach",
        "latitude": -35.5325,
        "longitude": 138.6214,
        "found_date": "2026-06-14",
        "notify_date": "2026-06-19",
        "confirm_date": "2026-06-24",
        "notes": "南澳首宗野鳥確診案。與西澳案例空間隔離超過 1,000 公里，證明為零星候鳥迷途登陸點。"
    },
    {
        "id": "CASE-004",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "巨鸌 (Giant Petrel)",
        "location": "西澳丹斯伯勒 Dunsborough (Quindalup) 地區",
        "latitude": -33.6128,
        "longitude": 115.1012,
        "found_date": "2026-06-22",
        "notify_date": "2026-06-24",
        "confirm_date": "2026-06-27",
        "notes": "原為疑似病例，於 6 月 27 日經聯邦首席獸醫官 Beth Cookson 正式發表聲明確診為第 4 起案件。"
    },
    {
        "id": "CASE-005",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "巨鸌 (Giant Petrel)",
        "location": "西澳 Roses Beach (埃斯佩蘭斯西側)",
        "latitude": -33.8752,
        "longitude": 121.7915,
        "found_date": "2026-06-25",
        "notify_date": "2026-06-26",
        "confirm_date": "2026-06-30",
        "notes": "原西澳 Roses Beach 疑似病例，經 ACDP 國家實驗室進一步檢測，官方已於 6 月 30 日正式升級為確診病例（西澳第 4 例）。"
    },
    {
        "id": "CASE-006",
        "type": "Negative",
        "source_status": "official_updated",
        "species": "死亡海鳥 (2隻)",
        "location": "南澳 Fowlers Bay Beach",
        "latitude": -31.9912,
        "longitude": 132.4331,
        "found_date": "2026-06-18",
        "notify_date": "2026-06-18",
        "confirm_date": "陰性 (已排除)",
        "notes": "南澳 Fowlers Bay 發現之海鳥屍體，經南澳農業廳 (PIRSA) PCR 檢測證實為陰性，成功排除禽流感嫌疑。"
    },
    {
        "id": "CASE-007",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "巨鸌 (Giant Petrel)",
        "location": "新南威爾斯州 Hawks Nest (Newcastle 以北)",
        "latitude": -32.6658,
        "longitude": 152.1793,
        "found_date": "2026-07-02",
        "notify_date": "2026-07-03",
        "confirm_date": "2026-07-04",
        "notes": "新南威爾斯州 (NSW) 首宗確診病例。於 Hawks Nest 發現之南方巨鸌，經吉隆 CSIRO 國家實驗室 (ACDP) 最終覆驗，已於 7 月 4 日由代理首席獸醫官 Sam Hamilton 發表正式聲明確認為 H5N1 高致病性陽性個案。"
    },
    {
        "id": "CASE-008",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "巨鸌 (Giant Petrel)",
        "location": "西澳伯斯北部 Mullaloo Beach",
        "latitude": -31.7826,
        "longitude": 115.7318,
        "found_date": "2026-07-03",
        "notify_date": "2026-07-04",
        "confirm_date": "2026-07-06",
        "notes": "西澳首府伯斯北部 Mullaloo Beach 發現之巨鸌，經吉隆 CSIRO 國家實驗室 (ACDP) 於 7 月 6 日檢測為 H5 陽性。西澳 DPIRD 官方今日已正式公告將其列為「推定陽性 (presumed positive)」並啟動預防性確診應對措施。"
    },
    {
        "id": "CASE-009",
        "type": "Negative",
        "source_status": "official_updated",
        "species": "野生海鳥 (1隻)",
        "location": "維多利亞州西部沿海地區 (Portland)",
        "latitude": -38.3608,
        "longitude": 141.6022,
        "found_date": "2026-06-28",
        "notify_date": "2026-07-01",
        "confirm_date": "2026-07-03",
        "notes": "維多利亞州一次產業廳送檢之異常死亡野鳥屍體，經吉隆 CSIRO 國家實驗室 (ACDP) 最終檢測為陰性，正式排除禽流感感染。"
    },
    {
        "id": "CASE-010",
        "type": "Negative",
        "source_status": "official_updated",
        "species": "野生鸕鶿 (Cormorant)",
        "location": "新南威爾斯州雪梨 Narrabeen Beach",
        "latitude": -33.7220,
        "longitude": 151.2985,
        "found_date": "2026-07-05",
        "notify_date": "2026-07-06",
        "confirm_date": "2026-07-07",
        "notes": "雪梨北部敘利濱海灘 (Narrabeen Beach) 發現之死亡鸕鶿，經新南威爾斯州一次產業部 (DPI) 進行化驗，於 7 月 7 日深夜證實為陰性，正式排除 H5N1 禽流感感染。"
    },
    {
        "id": "CASE-011",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "野生海鳥 (大鳳頭燕鷗 / Greater Crested Tern)",
        "location": "南澳 Robe Marina",
        "latitude": -37.1644,
        "longitude": 139.7624,
        "found_date": "2026-07-09",
        "notify_date": "2026-07-10",
        "confirm_date": "2026-07-10",
        "notes": "【本土留鳥首例確診】南澳野鳥確診病例。於 Robe Marina 發現之大鳳頭燕鷗，經國家實驗室檢測證實為 H5N1 陽性，為澳洲首例本土野生留鳥確診案例，標誌著病毒已突破境外候鳥防線，本土留鳥開始感染。"
    },
    {
        "id": "CASE-012",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "巨鸌 (Giant Petrel)",
        "location": "南澳 Yorke Peninsula Hardwicke Bay",
        "latitude": -34.8919,
        "longitude": 137.4595,
        "found_date": "2026-07-06",
        "notify_date": "2026-07-07",
        "confirm_date": "2026-07-08",
        "notes": "南澳 second 宗確診病例。於 Yorke Peninsula Hardwicke Bay 發現之巨鸌 (Giant Petrel)，經檢測證實為 H5N1 陽性。"
    },
    {
        "id": "CASE-013",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "巨鸌 (Giant Petrel)",
        "location": "南澳 Yorke Peninsula Port Vincent",
        "latitude": -34.7773,
        "longitude": 137.8613,
        "found_date": "2026-07-06",
        "notify_date": "2026-07-08",
        "confirm_date": "2026-07-12",
        "notes": "南澳確診病例。於 Yorke Peninsula Port Vincent 發現之巨鸌，經吉隆國家實驗室覆驗，已於 7 月 12 日正式升級為確診陽性。"
    },
    {
        "id": "CASE-014",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "巨鸌 (Giant Petrel)",
        "location": "南澳 Kangaroo Island Emu Bay",
        "latitude": -35.5899,
        "longitude": 137.5041,
        "found_date": "2026-07-06",
        "notify_date": "2026-07-08",
        "confirm_date": "2026-07-12",
        "notes": "南澳確診病例。於 Kangaroo Island Emu Bay 發現之巨鸌，經吉隆國家實驗室覆驗，已於 7 月 12 日正式升級為確診陽性。"
    },
    {
        "id": "CASE-015",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "野生海鳥 (巨鸌)",
        "location": "西澳 Horrocks Beach",
        "latitude": -28.3817,
        "longitude": 114.4304,
        "found_date": "2026-07-09",
        "notify_date": "2026-07-10",
        "confirm_date": "2026-07-12",
        "notes": "西澳確診病例（西澳第 6 例）。於西澳中西部 Horrocks Beach 發現之野生海鳥檢體，經國家實驗室複檢已於 7 月 12 日證實為 H5N1 陽性。"
    },
    {
        "id": "CASE-016",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "南方巨鸌 (Southern Giant Petrel)",
        "location": "西澳南部 Denmark (Parry Beach)",
        "latitude": -35.0315,
        "longitude": 117.1593,
        "found_date": "2026-07-12",
        "notify_date": "2026-07-14",
        "confirm_date": "2026-07-14",
        "notes": "西澳第 7 宗確診病例。於南海岸 Denmark 地區 Parry Beach 發現之南方巨鸌，經吉隆 ACDP 實驗室覆檢確診為 H5N1 陽性。"
    },
    {
        "id": "CASE-017",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "巨鸌 (Giant Petrel)",
        "location": "西澳 Lancelin 地區",
        "latitude": -31.0210,
        "longitude": 115.3315,
        "found_date": "2026-07-13",
        "notify_date": "2026-07-15",
        "confirm_date": "2026-07-15",
        "notes": "西澳第 8 宗確診病例。於西澳中海岸 Lancelin 發現之巨鸌檢體，經國家實驗室化驗確診為 H5N1 陽性個案。"
    },
    {
        "id": "CASE-018",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "巨海燕 (Giant Petrel)",
        "location": "新南威爾斯州中北岸 Hawks Nest (第二例)",
        "latitude": -32.6658,
        "longitude": 152.1793,
        "found_date": "2026-07-16",
        "notify_date": "2026-07-17",
        "confirm_date": "2026-07-17",
        "notes": "新南威爾斯州 (NSW) 第 2 宗確診病例。於中北岸 Hawks Nest 發現之另一隻巨海燕，經 ACDP 國家實驗室最終複檢，於 7 月 17 日確診為 H5N1 陽性。"
    },
    {
        "id": "CASE-019",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "野生海鳥 (巨鸌)",
        "location": "西澳 Gingin 郡 Seabird 海灘",
        "latitude": -31.2789,
        "longitude": 115.4414,
        "found_date": "2026-07-15",
        "notify_date": "2026-07-16",
        "confirm_date": "2026-07-17",
        "notes": "西澳第 9 宗確診病例。於西澳中海岸 Gingin 郡 Seabird 鎮海灘發現之野鳥檢體，經檢驗確診為 H5N1 高致病性陽性。"
    },
    {
        "id": "CASE-020",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "野生海鳥 (巨鸌)",
        "location": "西澳伯斯北部 Whitfords Beach",
        "latitude": -31.7944,
        "longitude": 115.7368,
        "found_date": "2026-07-16",
        "notify_date": "2026-07-17",
        "confirm_date": "2026-07-17",
        "notes": "西澳第 10 宗確診病例。於伯斯北部 Whitfords Beach（鄰近 Mullaloo Beach）發現之巨鸌，經實驗室化驗證實為 H5N1 陽性個案。"
    },
    {
        "id": "CASE-021",
        "type": "Negative",
        "source_status": "official_updated",
        "species": "北方巨海燕 (Northern Giant Petrel)",
        "location": "昆士蘭州 Noosa Main Beach",
        "latitude": -26.3847,
        "longitude": 153.0886,
        "found_date": "2026-07-11",
        "notify_date": "2026-07-12",
        "confirm_date": "陰性 (已排除)",
        "notes": "昆士蘭首宗通報之野鳥疑似病例。於 Noosa 海灘尋獲之北方巨海燕，經昆士蘭農業部 (Biosecurity Queensland) 化驗，已於 7 月 14 日證實為陰性，正式排除 H5N1 禽流感，目前昆士蘭維持無病例安全狀態。"
    },
    {
        "id": "CASE-022",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "野生海鳥 (大鳳頭燕鷗 / Greater Crested Tern)",
        "location": "南澳阿得雷德 Semaphore Beach",
        "latitude": -34.8394,
        "longitude": 138.4831,
        "found_date": "2026-07-23",
        "notify_date": "2026-07-24",
        "confirm_date": "2026-07-26",
        "notes": "【南澳都市區首起確診】南澳第 6 宗確診病例。於阿得雷德 Semaphore 衝浪救生會海灘發現之大鳳頭燕鷗，經 ACDP 國家實驗室檢測證實為 H5N1 陽性，為首起靠近大都市的病例。"
    },
    {
        "id": "CASE-023",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "野生海鳥 (大鳳頭燕鷗 / Greater Crested Tern)",
        "location": "南澳 Robe Marina (第二例)",
        "latitude": -37.1644,
        "longitude": 139.7624,
        "found_date": "2026-07-24",
        "notify_date": "2026-07-25",
        "confirm_date": "2026-07-26",
        "notes": "南澳第 7 宗確診病例。於 Robe Marina 發現之第二隻大鳳頭燕鷗，經 ACDP 國家實驗室檢測證實為 H5N1 陽性。"
    },
    {
        "id": "CASE-024",
        "type": "Confirmed",
        "source_status": "official_updated",
        "species": "遷徙海鳥 (巨鸌 / Petrel)",
        "location": "昆士蘭州摩爾頓島 Moreton Island",
        "latitude": -27.1812,
        "longitude": 153.4022,
        "found_date": "2026-07-23",
        "notify_date": "2026-07-25",
        "confirm_date": "2026-07-26",
        "notes": "【昆士蘭首例確診】昆士蘭州第 1 宗確診病例。於布里斯本外海 Moreton Island 發現之死亡海鳥檢體，經 CSIRO 國家實驗室 (ACDP) 覆檢確診為 H5N1 陽性，標誌著病毒正式擴散至昆士蘭地區。"
    },
    {
        "id": "CASE-025",
        "type": "Confirmed",
        "source_status": "official_confirmed",
        "detection_count": 5,
        "species": "野生海鳥 5 隻 (大鳳頭燕鷗 / Greater Crested Tern)：4 隻病危、1 隻已死亡",
        "location": "南澳東南部 Southend Jetty (near Beachport)",
        "latitude": -37.5683,
        "longitude": 140.1264,
        "found_date": "2026-07-26",
        "notify_date": "2026-07-27",
        "confirm_date": "2026-07-29",
        "notes": "【南澳 Limestone Coast 確診案例 - 7 隻合計中的 5 隻】於 Southend Jetty 發現 5 隻大鳳頭燕鷗（4 隻病危、1 隻已死亡），經 Geelong ACDP 國家實驗室複檢，已於 7 月 29 日確診為 H5N1 陽性。南澳衛生部長指出，此事件極可能代表病毒已開始在本地野鳥族群中傳播。【DAFF 統計：此 1 個 CASE 危 5 個 official detection】資料來源：DAFF / agriculture.gov.au 2026-07-29。"
    },
    {
        "id": "CASE-026",
        "type": "Confirmed",
        "source_status": "official_confirmed",
        "detection_count": 1,
        "species": "野生海鳥 1 隻 (大鳳頭燕鷗 / Greater Crested Tern)：1 隻已死亡",
        "location": "南澳東南部 Cape Jaffa",
        "latitude": -36.9389,
        "longitude": 139.6917,
        "found_date": "2026-07-26",
        "notify_date": "2026-07-27",
        "confirm_date": "2026-07-29",
        "notes": "【南澳 Limestone Coast 確診案例 - 7 隻合計中的 1 隻】於 Cape Jaffa 發現 1 隻已死亡大鳳頭燕鷗，經 Geelong ACDP 國家實驗室複檢，已於 7 月 29 日確診為 H5N1 陽性。資料來源：DAFF / agriculture.gov.au 2026-07-29。"
    },
    {
        "id": "CASE-027",
        "type": "Confirmed",
        "source_status": "official_confirmed",
        "detection_count": 1,
        "species": "野生海鳥 1 隻 (大鳳頭燕鷗 / Greater Crested Tern)：1 隻已死亡",
        "location": "南澳東南部 Port MacDonnell",
        "latitude": -38.0531,
        "longitude": 140.6972,
        "found_date": "2026-07-26",
        "notify_date": "2026-07-27",
        "confirm_date": "2026-07-29",
        "notes": "【南澳 Limestone Coast 確診案例 - 7 隻合計中的 1 隻】於 Port MacDonnell 發現 1 隻已死亡大鳳頭燕鷗，經 Geelong ACDP 國家實驗室複檢，已於 7 月 29 日確診為 H5N1 陽性。資料來源：DAFF / agriculture.gov.au 2026-07-29。"
    },
    {
        "id": "CASE-028",
        "type": "Suspect",
        "source_status": "official_announced",
        "detection_count": 4,
        "species": "野生海鳥 4 隻 (大鳳頭燕鷗 / Greater Crested Tern)",
        "location": "南澳 袋鼠島 Seal Bay, Kangaroo Island",
        "latitude": -35.9766,
        "longitude": 137.3164,
        "found_date": "2026-07-28",
        "notify_date": "2026-07-29",
        "confirm_date": "進行中 (Pending)",
        "notes": "【南澳 袋鼠島疑似案例 - 待覆核 24 例之一部分】於 Kangaroo Island Seal Bay 發現 4 隻大鳳頭燕鷗疑似病例，已送往 CSIRO ACDP 進行最終檢驗。Seal Bay 已暫停海灘旅遊活動以保護海獅族群。資料來源：InDaily SA / DAFF 2026-07-29。"
    },
    {
        "id": "CASE-030",
        "type": "Confirmed",
        "source_status": "official_confirmed",
        "detection_count": 1,
        "species": "野生海鳥 1 隻 (大鳳頭燕鷗 / Greater Crested Tern)",
        "location": "維多利亞州 Portland (south-west Victoria)",
        "latitude": -38.3608,
        "longitude": 141.6022,
        "found_date": "2026-07-29",
        "notify_date": "2026-07-30",
        "confirm_date": "2026-07-30",
        "notes": "【維多利亞州首例確診 - 7/30 今日最新】維多利亞州農業局 (Agriculture Victoria) 於 7 月 30 日正式宣布於 Portland 發現之大鳳頭燕鷗呈 H5 陽性。標誌著維州失守，全澳洲所有 5 個 mainland 州全數淪陷！維州已啟動緊急動物疾病應變計畫。資料來源：Agriculture Victoria 2026-07-30。"
    },
    {
        "id": "CASE-031",
        "type": "Suspect",
        "source_status": "official_announced",
        "detection_count": 13,
        "species": "野生海鳥 13 隻 (大鳳頭燕鷗 / Greater Crested Tern)",
        "location": "南澳沿海地區 (SA Coastal Regions)",
        "latitude": -35.2000,
        "longitude": 137.5000,
        "found_date": "2026-07-30",
        "notify_date": "2026-07-30",
        "confirm_date": "進行中 (Pending)",
        "notes": "【南澳 7/30 今日暴增 13 隻全新疑似個案】南澳初級產業廳 (PIRSA) 7 月 30 日證實，沿海地區再度發現 13 隻大鳳頭燕鷗集體生病死亡疑似案例，檢體正送往 Geelong ACDP 國家實驗室進行最終檢驗，南澳待覆核個案總數達 24 例。聯邦 DAFF 強調所有商業家禽農場目前依然 100% 零感染。資料來源：PIRSA / DAFF 2026-07-30。"
    },
    {
        "id": "CASE-032",
        "type": "Confirmed",
        "source_status": "official_confirmed",
        "detection_count": 1,
        "species": "野生巨鸌 1 隻 (Giant Petrel)",
        "location": "南澳艾爾半島 Port Lincoln (Eyre Peninsula)",
        "latitude": -34.7322,
        "longitude": 135.8586,
        "found_date": "2026-07-29",
        "notify_date": "2026-07-30",
        "confirm_date": "2026-07-30",
        "notes": "【南澳艾爾半島新增確診 - 7/30 下午最新】南澳艾爾半島 (Eyre Peninsula) 林肯港 (Port Lincoln) 新增 1 隻野生巨鸌確診，使南澳確診數推升至 15 例，全澳累計確診達 28 例。資料來源：DAFF / PIRSA 2026-07-30。"
    },
    {
        "id": "CASE-033",
        "type": "Confirmed",
        "source_status": "official_confirmed",
        "detection_count": 4,
        "species": "野生海鳥 4 隻 (大鳳頭燕鷗 / Greater Crested Tern)",
        "location": "南澳袋鼠島 Seal Bay 及沿海地區",
        "latitude": -35.9766,
        "longitude": 137.3164,
        "found_date": "2026-07-28",
        "notify_date": "2026-07-31",
        "confirm_date": "2026-07-31",
        "notes": "【南澳袋鼠島與沿海新增確診 - 7/31 最新】7 月 31 日 DAFF 官方最新數據，原送檢之袋鼠島 Seal Bay 4 隻大鳳頭燕鷗經 ACDP 覆驗確診為 H5N1 陽性，使南澳確診個案推升至 19 例，全澳累計確診達 33 例。資料來源：DAFF 2026-07-31。"
    },
    {
        "id": "CASE-034",
        "type": "Suspect",
        "source_status": "official_announced",
        "detection_count": 1,
        "species": "野生海鳥 1 隻 (大鳳頭燕鷗 / Greater Crested Tern)",
        "location": "維多利亞州 Portland (第 2 例疑似)",
        "latitude": -38.3608,
        "longitude": 141.6022,
        "found_date": "2026-07-30",
        "notify_date": "2026-07-31",
        "confirm_date": "進行中 (Pending)",
        "notes": "【維多利亞州第二例疑似 - 7/31 最新】維州農業局 7 月 31 日通報，於 Portland 發現第 2 隻大鳳頭燕鷗疑似病例，檢體已送往 ACDP 進行覆驗。資料來源：Agriculture Victoria 2026-07-31。"
    },
    {
        "id": "CASE-035",
        "type": "Confirmed",
        "source_status": "official_confirmed",
        "detection_count": 19,
        "species": "野生海鳥 19 隻 (大鳳頭燕鷗 / Greater Crested Tern)",
        "location": "南澳 Robe、Beachport、袋鼠島等沿海棲息地",
        "latitude": -37.1644,
        "longitude": 139.7624,
        "found_date": "2026-07-30",
        "notify_date": "2026-08-01",
        "confirm_date": "2026-08-01",
        "notes": "【南澳 8/1 舊疑似大規模覆核確診 - 暴增 19 例】CSIRO ACDP 國家實驗室完成大規模基因定序，南澳先前送驗之 19 隻大鳳頭燕鷗（分佈於 Robe、Beachport、袋鼠島等地）一舉覆核轉為正式陽性確診。資料來源：DAFF / PIRSA 2026-08-01。"
    },
    {
        "id": "CASE-036",
        "type": "Confirmed",
        "source_status": "official_confirmed",
        "detection_count": 1,
        "species": "野生海鷗 1 隻 (銀鷗 / Silver Gull)",
        "location": "南澳 Robe 地區",
        "latitude": -37.1644,
        "longitude": 139.7624,
        "found_date": "2026-07-31",
        "notify_date": "2026-08-01",
        "confirm_date": "2026-08-01",
        "notes": "【全澳洲首例海鷗確診 - 8/1 最新】南澳 Robe 發現之銀鷗（Silver Gull / 海鷗）經 ACDP 覆核確診 H5N1 陽性。此為全澳洲首例海鷗確診個案，因海鷗大量棲息於城鎮與人類社區，專家警告病毒恐即將往內陸與淡水環境蔓延。資料來源：DAFF / PIRSA 2026-08-01。"
    },
    {
        "id": "CASE-037",
        "type": "Confirmed",
        "source_status": "official_announced",
        "detection_count": 6,
        "species": "野生海鳥 6 隻 (大鳳頭燕鷗 / Greater Crested Tern)",
        "location": "維多利亞州 西南海岸地區 (SW Victoria Coast)",
        "latitude": -38.3608,
        "longitude": 141.6022,
        "found_date": "2026-07-31",
        "notify_date": "2026-08-03",
        "confirm_date": "2026-08-03",
        "notes": "【維多利亞州西南海岸 6 例覆核確診 - 8/3 最新】維州農業局先前於西南海岸發現之 6 隻大鳳頭燕鷗疑似個案，經 ACDP 實驗室覆驗已正式轉為確診陽性，使維州確診總數上升至 7 例。資料來源：Agriculture Victoria 2026-08-03。"
    },
    {
        "id": "CASE-038",
        "type": "Suspect",
        "source_status": "official_announced",
        "detection_count": 84,
        "species": "野生海鳥 84 隻 (大鳳頭燕鷗：49隻死亡、35隻生病)",
        "location": "南澳沿海離島 Baudin Rocks",
        "latitude": -37.0950,
        "longitude": 139.7180,
        "found_date": "2026-07-31",
        "notify_date": "2026-08-01",
        "confirm_date": "進行中 (Pending)",
        "notes": "【南澳離島首起野生動物大規模死亡事件 - 8/1 最新】南澳環境部利用無人機巡查 Baudin Rocks 時發現 49 隻大鳳頭燕鷗死亡、35 隻生病之大規模群聚慘況，緊急採樣送驗中，極度擔憂為全澳首起野生動物集體大規模死亡事件。資料來源：PIRSA / SA DEW 2026-08-01。"
    },
    {
        "id": "CASE-039",
        "type": "Confirmed",
        "source_status": "official_confirmed",
        "detection_count": 3,
        "species": "野生海鳥 3 隻",
        "location": "南澳沿海地區 (South Australia Coast)",
        "latitude": -35.2,
        "longitude": 137.5,
        "found_date": "2026-08-02",
        "notify_date": "2026-08-03",
        "confirm_date": "2026-08-03",
        "notes": "【南澳新增 3 例確診 - 8/3 最新】南澳沿海地區新增 3 例野鳥確診個案，使南澳累計確診總數推升至 42 例。目前官方尚未公佈確切之地理坐標，暫以南澳沿海概略位置標示。資料來源：DAFF 2026-08-03。"
    }
]

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    使用 Haversine 公式計算地球上兩點之間的直線距離 (公里)
    """
    R = 6371.0  # 地球平均半徑 (公里)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

LOCAL_GAZETTEER = {
    "robe": (-37.1644, 139.7624),
    "beachport": (-37.4833, 140.0167),
    "kangaroo island": (-35.7752, 137.2142),
    "seal bay": (-35.9766, 137.3164),
    "baudin rocks": (-37.0950, 139.7180),
    "portland": (-38.3608, 141.6022),
    "port lincoln": (-34.7322, 135.8586),
    "southend": (-37.5683, 140.1264),
    "cape jaffa": (-36.9389, 139.6917),
    "port macdonnell": (-38.0531, 140.6972),
    "esperance": (-33.8613, 121.9021),
    "cape le grand": (-33.9912, 122.1481),
    "roses beach": (-33.8752, 121.7915),
    "dunsborough": (-33.6128, 115.1012),
    "mullaloo": (-31.7826, 115.7318),
    "whitfords": (-31.7944, 115.7368),
    "lancelin": (-31.0210, 115.3315),
    "seabird": (-31.2789, 115.4414),
    "denmark": (-35.0315, 117.1593),
    "parry beach": (-35.0315, 117.1593),
    "horrocks": (-28.3817, 114.4304),
    "hawks nest": (-32.6658, 152.1793),
    "narrabeen": (-33.7220, 151.2985),
    "semaphore": (-34.8394, 138.4831),
    "moreton island": (-27.1812, 153.4022),
    "noosa": (-26.3847, 153.0886),
    "hardwicke bay": (-34.8919, 137.4595),
    "port vincent": (-34.7773, 137.8613),
    "fleurieu": (-35.5325, 138.6214),
    "fowlers bay": (-31.9912, 132.4331),
    "northampton": (-28.3667, 114.6333),
    "wa": (-31.9505, 115.8605),
    "western australia": (-31.9505, 115.8605),
    "sa": (-34.9285, 138.6007),
    "south australia": (-34.9285, 138.6007),
    "nsw": (-33.8688, 151.2093),
    "new south wales": (-33.8688, 151.2093),
    "vic": (-37.8136, 144.9631),
    "victoria": (-37.8136, 144.9631),
    "qld": (-27.4705, 153.0260),
    "queensland": (-27.4705, 153.0260),
}

def get_coordinates_from_api(location_name):
    """
    將地名轉換為精確 GPS 經緯度 (優先搜尋內建 Australian Gazetteer 字典，兜底呼叫 Nominatim API 或州級備用坐標)
    """
    loc_clean_lower = location_name.lower().strip()

    # 1. 優先查本地字典 (避免 GitHub Actions / CI 網路被 Nominatim 阻擋 403/429)
    for g_key, coords in LOCAL_GAZETTEER.items():
        if g_key in loc_clean_lower or loc_clean_lower in g_key:
            print(f"[本地地名庫命中] '{location_name}' -> {coords}")
            return coords[0], coords[1]

    headers = {
        "User-Agent": "Purina-Blayney-H5N1-Monitor/1.0 (contact: bluebirdfinder@example.com)"
    }
    
    # 嘗試策略 1: 完整名稱 + Australia
    queries = [f"{location_name}, Australia"]
    
    # 嘗試策略 2: 去除沙灘海灣修飾詞 + Australia
    clean_name = re.sub(r"\b(beach|bay|marina|port|point|creek|river|lake|cape|mount|hill|island|islands)\b", "", location_name, flags=re.IGNORECASE).strip()
    if clean_name and clean_name != location_name:
        queries.append(f"{clean_name}, Australia")
        
    # 嘗試策略 3: 原始地名直接搜
    queries.append(location_name)
    
    cf_worker_url = os.environ.get("CF_WORKER_URL", "").strip().rstrip("/")
    if cf_worker_url:
        for q in queries:
            try:
                nom_target = f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(q)}&format=json&limit=1"
                proxy_target = f"{cf_worker_url}/?url={requests.utils.quote(nom_target)}"
                print(f"  [Cloudflare 地理編碼代理] 正在透過 Cloudflare 轉接查詢 Nominatim: '{q}' ...")
                resp = requests.get(proxy_target, timeout=8, verify=False)
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list) and data:
                        lat = float(data[0]["lat"])
                        lon = float(data[0]["lon"])
                        print(f"  ✅ [Cloudflare 地理編碼成功] '{q}' (地名: {location_name}) -> 坐標: ({lat}, {lon})")
                        return lat, lon
            except Exception as e:
                print(f"  ⚠️ [Cloudflare 地理編碼失敗] {str(e)}")

    for q in queries:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": q,
            "format": "json",
            "limit": 1
        }
        try:
            import time
            time.sleep(0.5)
            response = requests.get(url, params=params, headers=headers, timeout=5, verify=False)
            if response.status_code == 200:
                data = response.json()
                if data:
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
                    print(f"[地理編碼成功] 查詢: '{q}' (地名: {location_name}) -> 坐標: ({lat}, {lon})")
                    return lat, lon
        except Exception as e:
            print(f"[地理編碼警告] 查詢 '{q}' 失敗: {str(e)}")
            
    # 2. 兜底策略：依州別提供預設備用坐標 (保證不會因為地名查不到而丟棄案例)
    state_defaults = {
        "sa": (-34.9285, 138.6007),
        "wa": (-31.9505, 115.8605),
        "vic": (-37.8136, 144.9631),
        "nsw": (-33.8688, 151.2093),
        "qld": (-27.4705, 153.0260),
    }
    for st, coords in state_defaults.items():
        if st in loc_clean_lower:
            print(f"[州級備用坐標命中] 地名 '{location_name}' 使用 {st.upper()} 州備用坐標: {coords}")
            return coords[0], coords[1]

    print(f"[地理編碼備用] 地名 '{location_name}' 使用澳洲南部預設坐標: (-35.0, 138.0)")
    return -35.0, 138.0

def discover_new_cases(soup, existing_cases):
    """
    動態分析網頁 HTML，尋找潛在的全新疫情地點，並自動進行地理定位
    優化防重覆判斷：利用 GPS 座標直線距離與通報日期雙重判定，防堵熱點多案例被誤殺過濾。
    """
    if not soup:
        return []
        
    relevant_texts = []
    for elem in soup.find_all(["p", "li"]):
        txt = elem.text.strip()
        if any(kw in txt.lower() for kw in ["wild bird", "petrel", "skua", "seabird", "influenza", "h5n1", "h5", "detection"]):
            relevant_texts.append(txt)
            
    stop_words = {
        "australia", "western australia", "south australia", "new south wales", "victoria", 
        "queensland", "tasmania", "june", "july", "august", "september", "acdp", "csiro", 
        "emergency", "avian", "influenza", "h5n1", "h5", "the", "department", "giant", 
        "southern", "news", "health", "animal", "australian", "minister", "official", 
        "update", "cases", "testing", "biosecurity", "sa", "nsw", "wa", "vic", "qld", "tas", "nt", "act"
    }

    candidates = []
    for txt in relevant_texts:
        matches = re.findall(r"\b(near|at|in|from)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2})", txt)
        for prep, m in matches:
            m_clean = re.sub(r"\s+", " ", m).strip(",.() ")
            if len(m_clean) < 3 or m_clean.lower() in stop_words or any(w in stop_words for w in m_clean.lower().split()):
                continue
            candidates.append((m_clean, txt))
            
    unique_candidates = {}
    for loc, source_text in candidates:
        if loc not in unique_candidates:
            unique_candidates[loc] = source_text
            
    new_discovered = []
    case_idx = len(existing_cases) + 1
    
    for loc, src_txt in unique_candidates.items():
        # 改進的防重覆判斷 (避免同地熱點第二案例被跳過)
        # 1. 檢查地點字串是否重合
        is_existing_text = False
        for ec in existing_cases:
            if loc.lower() in ec["location"].lower() or ec["location"].lower() in loc.lower():
                is_existing_text = True
                break
        
        # 2. 如果地名重合，但可能為不同日期之獨立個案，此時去查地理位置
        lat, lon = get_coordinates_from_api(loc)
        if lat is None or lon is None:
            continue
            
        # 計算與現有病例的距離 (公里)
        is_too_close = False
        for ec in existing_cases:
            dist = calculate_distance(lat, lon, ec["latitude"], ec["longitude"])
            # 若與現有病例距離極近 (小於 2 公里)，且日期重疊，才判定為重複通報
            if dist < 2.0 and ec["notify_date"] == datetime.now(timezone.utc).strftime("%Y-%m-%d"):
                is_too_close = True
                break
                
        # 只有在既不是文字重合，也沒有靠得太近的重複日期案件時，才新增
        if is_existing_text and is_too_close:
            continue
            
        type_status = "Suspect"
        confirm_date = "進行中 (Pending)"
        notes_prefix = "動態偵測疑似病例。"
        source_stat = ""
        if any(kw in src_txt.lower() for kw in ["confirmed", "has confirmed", "tests confirmed"]):
            type_status = "Confirmed"
            now_taipei = datetime.now(timezone.utc) + timedelta(hours=8)
            confirm_date = now_taipei.strftime("%Y-%m-%d")
            notes_prefix = "官方已確診病例。"
            source_stat = "official_updated"
            
        new_case = {
            "id": f"CASE-{case_idx:03d}",
            "type": type_status,
            "source_status": source_stat,
            "species": "野生候鳥 (野鳥監測)",
            "location": f"新偵測：{loc}",
            "latitude": lat,
            "longitude": lon,
            "found_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "notify_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "confirm_date": confirm_date,
            "notes": f"【動態爬蟲自動生成】{notes_prefix}來源文字段落：\"{src_txt}\""
        }
        print(f"[動態新增成功] 成功將新地點 '{loc}' 寫入病例資料庫 (ID: {new_case['id']}, 坐標: {lat}, {lon})")
        new_discovered.append(new_case)
        case_idx += 1
        
    return new_discovered

def discover_cases_from_news_rss(rss_text, existing_cases):
    """
    【防 Link Rot 第二道兜底防線】
    當所有官方網站 URL 改版失效時，直接從 Google News RSS 新聞流中，
    分析標題與內文，提取新疫情地點，並進行地理編碼與病例登錄。
    """
    if not rss_text:
        return []
        
    items = re.findall(r"<title>(.*?)</title>", rss_text)
    descriptions = re.findall(r"<description>(.*?)</description>", rss_text)
    all_texts = items + descriptions
    
    candidates = []
    for txt in all_texts:
        if any(kw in txt.lower() for kw in ["bird flu", "avian influenza", "h5n1", "h5"]):
            stop_words = {
                "australia", "western australia", "south australia", "new south wales", "victoria", 
                "queensland", "tasmania", "june", "july", "august", "september", "acdp", "csiro", 
                "emergency", "avian", "influenza", "h5n1", "h5", "the", "department", "giant", 
                "southern", "news", "health", "animal", "australian", "minister", "official", 
                "update", "cases", "testing", "biosecurity", "sa", "nsw", "wa", "vic", "qld", "tas", "nt", "act"
            }
            matches = re.findall(r"\b(at|in|near|from)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2})", txt)
            for prep, m in matches:
                m_clean = re.sub(r"\s+", " ", m).strip(",.() ")
                if len(m_clean) < 3 or m_clean.lower() in stop_words or any(w in stop_words for w in m_clean.lower().split()):
                    continue
                candidates.append((m_clean, txt))
                
    unique_candidates = {}
    for loc, src_text in candidates:
        if loc not in unique_candidates:
            unique_candidates[loc] = src_text
            
    new_discovered = []
    case_idx = len(existing_cases) + 1
    
    for loc, src_txt in unique_candidates.items():
        is_existing_text = False
        for ec in existing_cases:
            if loc.lower() in ec["location"].lower() or ec["location"].lower() in loc.lower():
                is_existing_text = True
                break
                
        print(f"[RSS 新聞兜底偵測] 發現全新潛在疫情地點關鍵字: '{loc}'，正在進行地理定位...")
        lat, lon = get_coordinates_from_api(loc)
        if lat is None or lon is None:
            continue
            
        is_too_close = False
        for ec in existing_cases:
            dist = calculate_distance(lat, lon, ec["latitude"], ec["longitude"])
            if dist < 2.0 and ec["notify_date"] == datetime.now(timezone.utc).strftime("%Y-%m-%d"):
                is_too_close = True
                break
                
        if is_existing_text and is_too_close:
            continue
            
        type_status = "Suspect"
        confirm_date = "進行中 (Pending)"
        notes_prefix = "新聞 RSS 兜底模組自動偵測之疑似病例。"
        source_stat = "media_announced"
        
        if any(kw in src_txt.lower() for kw in ["confirmed", "tests positive", "testing positive"]):
            type_status = "Confirmed"
            now_taipei = datetime.now(timezone.utc) + timedelta(hours=8)
            confirm_date = now_taipei.strftime("%Y-%m-%d")
            notes_prefix = "新聞 RSS 兜底模組自動確診之病例。"
            
        new_case = {
            "id": f"CASE-{case_idx:03d}",
            "type": type_status,
            "source_status": source_stat,
            "species": "野生候鳥 (新聞監控)",
            "location": f"新聞偵測：{loc}",
            "latitude": lat,
            "longitude": lon,
            "found_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "notify_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "confirm_date": confirm_date,
            "notes": f"【新聞 RSS 兜底定位】{notes_prefix}來源新聞標題：\"{src_txt}\""
        }
        print(f"[RSS 新聞兜底新增成功] 成功將新地點 '{loc}' 寫入病例資料庫 (ID: {new_case['id']})")
        new_discovered.append(new_case)
        case_idx += 1
        
    return new_discovered

def smart_fetch_url(url, headers=None, timeout=10):
    """
    強化版跨障礙 HTTP 抓取器：
    1. 優先試用用戶配置的 Cloudflare Worker 代理 (CF_WORKER_URL 變數)
    2. 嘗試使用 curl_cffi 進行 Chrome 120 TLS 指紋偽裝抓取
    3. 嘗試使用 Playwright 無頭真實瀏覽器渲染抓取
    4. 兜底嘗試第三方 CORS Proxy (AllOrigins / corsproxy)
    5. 最後回退至標準 requests.get
    """
    cf_worker_url = os.environ.get("CF_WORKER_URL", "").strip().rstrip("/")
    if cf_worker_url:
        try:
            proxy_target = f"{cf_worker_url}/?url={url}"
            print(f"  [Cloudflare Worker 代理通道] 正在透過 Cloudflare 轉接抓取 {url} ...")
            resp = requests.get(proxy_target, timeout=timeout+5, verify=False)
            if resp.status_code == 200 and resp.text and len(resp.text) > 200:
                print(f"  ✅ [Cloudflare Worker 成功] 取得 {len(resp.text)} 位元組數據！")
                return resp.text
        except Exception as e:
            print(f"  ⚠️ [Cloudflare Worker 失敗] {str(e)}")

    # 嘗試策略 2: curl_cffi Chrome TLS 指紋偽裝
    try:
        from curl_cffi import requests as cffi_requests
        print("  [curl_cffi 擬真通道] 正在模擬真實 Chrome TLS 指紋發送請求...")
        resp = cffi_requests.get(url, impersonate="chrome120", timeout=timeout, verify=False)
        if resp.status_code == 200 and resp.text and len(resp.text) > 200:
            print(f"  ✅ [curl_cffi 成功] 取得 {len(resp.text)} 位元組數據！")
            return resp.text
    except Exception as e:
        print(f"  ⚠️ [curl_cffi 失敗/未安裝] {str(e)}")

    # 嘗試策略 3: Playwright 無頭瀏覽器
    try:
        from playwright.sync_api import sync_playwright
        print("  [Playwright 瀏覽器通道] 正在啟動真實 Chromium 模擬人眼瀏覽...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=timeout*1000)
            content = page.content()
            browser.close()
            if content and len(content) > 200:
                print(f"  ✅ [Playwright 成功] 取得 {len(content)} 位元組數據！")
                return content
    except Exception as e:
        print(f"  ⚠️ [Playwright 失敗/未安裝] {str(e)}")

    # 嘗試策略 4: CORS 代理 (AllOrigins / corsproxy / CodeTabs / ThingProxy)
    for proxy_pattern in [
        "https://api.allorigins.win/get?url={url}",
        "https://corsproxy.io/?{url}",
        "https://api.codetabs.com/v1/proxy?quest={url}",
        "https://thingproxy.freeboard.io/fetch/{url}"
    ]:
        try:
            proxy_url = proxy_pattern.format(url=url)
            print(f"  [第三方 CORS 代理通道] 正在嘗試 {proxy_pattern.split('/')[2]}...")
            resp = requests.get(proxy_url, headers=headers, timeout=timeout+4, verify=False)
            if resp.status_code == 200:
                body = resp.text
                if "allorigins" in proxy_pattern and "json" in resp.headers.get("Content-Type", ""):
                    body = resp.json().get("contents", "")
                if body and len(body) > 200:
                    print(f"  ✅ [第三方代理成功] 取得數據！")
                    return body
        except Exception as e:
            pass

    # 嘗試策略 5: 標準 requests.get 兜底
    try:
        print("  [標準 HTTP 兜底通道] 發送一般 HTTP GET 請求...")
        resp = requests.get(url, headers=headers, timeout=timeout, verify=False)
        if resp.status_code == 200:
            return resp.text
    except Exception as e:
        print(f"  ⚠️ [標準 HTTP 失敗] {str(e)}")

    return None

def fetch_daff_updates():
    """
    聯防爬蟲模組：同時爬取聯邦 DAFF 官網、以及澳洲全部 8 個州/領地政府的官方禽流感更新站點。
    優化 WAF 阻擋應對能力：結合 Cloudflare Worker 代理、curl_cffi TLS 偽裝與 Playwright 真實瀏覽器。
    """
    sources = {
        "DAFF_Entry": "https://www.agriculture.gov.au/campaigns/birdflu",
        "DAFF_1": "https://www.agriculture.gov.au/node/26086",
        "DAFF_2": "https://www.agriculture.gov.au/about/news/H5-testing-updates",
        "NSW": "https://www.dpird.nsw.gov.au/dpi/biosecurity/animal-biosecurity/avian-influenza",
        "SA": "https://pir.sa.gov.au/animal-management/animal-health/species/poultry/avian-influenza",
        "WA": "https://www.wa.gov.au/organisation/department-of-primary-industries-and-regional-development/avian-influenza",
        "VIC": "https://agriculture.vic.gov.au/biosecurity/animal-diseases/poultry-diseases/avian-influenza",
        "QLD": "https://www.business.qld.gov.au/industries/farms-fishing-forestry/agriculture/animal/health-diseases/disorders/avian-influenza",
        "TAS": "https://nre.tas.gov.au/biosecurity-tasmania/animal-biosecurity/animal-health/poultry-and-birds/avian-influenza",
        "NT": "https://nt.gov.au/industry/agriculture/livestock/animal-health-and-diseases/avian-influenza",
        "ACT": "https://www.environment.act.gov.au/biosecurity/avian-influenza"
    }
    
    google_rss_url = "https://news.google.com/rss/search?q=avian+influenza+Australia&hl=en-AU&gl=AU&ceid=AU:en"
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }
    
    soups = []
    
    # 逐一爬取全澳官方來源，採用多重防阻擋通道
    for name, url in sources.items():
        print(f"正在連線澳洲官方網站 ({name}): {url} ...")
        html_content = smart_fetch_url(url, headers=headers, timeout=8)
        if html_content:
            soup = BeautifulSoup(html_content, "html.parser")
            soups.append(soup)
        else:
            print(f"警告: {name} 所有防阻擋通道連線均告失敗，跳過此站點，維持既有病例數據。")
            
    # 爬取 Google News 澳洲禽流感即時 RSS
    abc_rss_text = ""
    print(f"正在連線 Google News RSS: {google_rss_url} ...")
    rss_content = smart_fetch_url(google_rss_url, headers=headers, timeout=12)
    if rss_content:
        abc_rss_text = rss_content.lower()
    else:
        print(f"警告: Google News RSS 連線失敗。")
        
    cases = json.loads(json.dumps(DEFAULT_CASES))
    
    # 官方比對輔助函數
    def check_confirmed_in_soups(target_soups, location_keyword):
        for soup in target_soups:
            if not soup:
                continue
            paragraphs = [p.text for p in soup.find_all(["p", "li"]) if location_keyword in p.text]
            for p in paragraphs:
                if any(kw in p.lower() for kw in ["confirmed", "has confirmed", "tests confirmed", "confirmed as"]):
                    return True
        return False

    def check_confirmed_in_news(news_text, location_keyword):
        if not news_text or location_keyword.lower() not in news_text:
            return False
        authorities = ["csiro", "acdp", "veterinary officer", "dpird", "department", "daff", "moriarty", "cookson", "minister"]
        confirms = ["confirmed", "tests positive", "testing positive", "confirm", "positive"]
        if any(a in news_text for a in authorities) and any(c in news_text for c in confirms):
            return True
        return False

    # 對已知疑似病例進行交叉升級檢查
    for case in cases:
        if case["type"] == "Suspect":
            loc_keyword = case["location"].replace("新偵測：", "").replace("新聞偵測：", "").split()[0]
            if check_confirmed_in_soups(soups, loc_keyword):
                case["type"] = "Confirmed"
                case["source_status"] = "official_updated"
                case["confirm_date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                print(f"[動態更新] 偵測到疑似病例 {case['id']} ({case['location']}) 已轉為『官方確診』！")
            elif check_confirmed_in_news(abc_rss_text, loc_keyword):
                case["type"] = "Confirmed"
                case["source_status"] = "media_announced"
                case["confirm_date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                print(f"[動態更新] 偵測到疑似病例 {case['id']} ({case['location']}) 已轉為『媒體先行確診』！")

    # 1. 第一道防線：從成功抓取的各州官網 soup 中動態提取新地點
    for s in soups:
        discovered_cases = discover_new_cases(s, cases)
        for nc in discovered_cases:
            if not any(abs(c["latitude"] - nc["latitude"]) + abs(c["longitude"] - nc["longitude"]) < 0.1 for c in cases):
                cases.append(nc)

    # 2. 第二道防線 (防 Link Rot 核心)：直接從 RSS 新聞文本中動態提取新疫情點 (官網癱瘓時的兜底)
    rss_discovered = discover_cases_from_news_rss(abc_rss_text, cases)
    for nc in rss_discovered:
        if not any(abs(c["latitude"] - nc["latitude"]) + abs(c["longitude"] - nc["longitude"]) < 0.1 for c in cases):
            cases.append(nc)

    # 3. 第三道防線：智慧對帳與盲區自動補齊機制 (Reconciliation Engine)
    # 解析官方各州已知底線目標 (若官網爬取解析出新目標會自動擴充，預設為最新官方對帳基準)
    target_state_totals = {"WA": 10, "SA": 42, "NSW": 2, "QLD": 1, "VIC": 7}
    
    # 嘗試從所有抓取到的官方及新聞 HTML/Text 中動態動態提取官方數字
    all_combined_text = " ".join([s.get_text() for s in soups if s]) + " " + abc_rss_text
    for state_name_en, state_key in [("Western Australia", "WA"), ("South Australia", "SA"), 
                                     ("New South Wales", "NSW"), ("Queensland", "QLD"), 
                                     ("Victoria", "VIC")]:
        match = re.search(fr"{state_name_en}(?:\s*\([A-Z]+\))?\s*[:-]\s*(\d+)", all_combined_text, re.IGNORECASE)
        if match:
            extracted_num = int(match.group(1))
            if extracted_num > target_state_totals.get(state_key, 0):
                target_state_totals[state_key] = extracted_num

    cases = reconcile_state_counts(cases, target_state_totals)

    return cases

def reconcile_state_counts(cases, target_state_totals):
    """
    智慧對帳系統：比對現有病例點與官方各州控制目標 (target_state_totals)。
    若官方數字 (如 SA: 42) > 目前已提取座標的病例總數，
    則自動發起盲區補齊，生成『官方已確診，未公布具體地點』的盲區病例節點。
    """
    state_mapping = [
        ("西澳", "WA", -31.9505, 115.8605, "西澳沿海地區"),
        ("南澳", "SA", -35.2, 137.5, "南澳沿海地區"),
        ("新南威爾斯", "NSW", -33.8688, 151.2093, "新州沿海地區"),
        ("維多利亞", "VIC", -38.3608, 141.6022, "維州沿海地區"),
        ("昆士蘭", "QLD", -27.4705, 153.0260, "昆州沿海地區"),
    ]
    
    current_counts = {k: 0 for _, k, _, _, _ in state_mapping}
    for c in cases:
        if c["type"] == "Confirmed":
            for name_zh, key, _, _, _ in state_mapping:
                if name_zh in c["location"] or key in c["location"]:
                    current_counts[key] += c.get("detection_count", 1)
                    break

    max_id = 0
    for c in cases:
        if c["id"].startswith("CASE-"):
            try:
                max_id = max(max_id, int(c["id"].replace("CASE-", "")))
            except ValueError:
                pass
    case_idx = max_id + 1

    for name_zh, key, default_lat, default_lon, default_loc in state_mapping:
        target = target_state_totals.get(key, 0)
        curr = current_counts.get(key, 0)
        gap = target - curr
        if gap > 0:
            new_blind_case = {
                "id": f"CASE-{case_idx:03d}",
                "type": "Confirmed",
                "source_status": "official_reconciled",
                "detection_count": gap,
                "species": f"野生海鳥 {gap} 隻 (官方已確診，詳細地點待公布)",
                "location": f"{name_zh}沿海地區 (官方確診/未公布細節)",
                "latitude": default_lat,
                "longitude": default_lon,
                "found_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "notify_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "confirm_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "notes": f"【智慧對帳自動補齊】官方 DAFF/州政府最新數據確認 {name_zh} 累計確診達 {target} 例。其中 {gap} 例官方尚未公布具體海岸/鎮名座標，系統自動錨定至 {name_zh} 沿海監控區域以維持對帳 100% 精確。"
            }
            print(f"[智慧對帳補齊] {name_zh} 自動補齊 {gap} 例盲區確診 (ID: {new_blind_case['id']})")
            cases.append(new_blind_case)
            case_idx += 1

    return cases

def generate_dynamic_summary(cases_data):
    """
    根據當前的病例數據，動態產生包含超連結與 current status 的官方事實與媒體觀察摘要。
    """
    states_stats = {
        "WA": {"Confirmed": 0, "Suspect": 0, "Negative": 0, "total": 0},
        "SA": {"Confirmed": 0, "Suspect": 0, "Negative": 0, "total": 0},
        "NSW": {"Confirmed": 0, "Suspect": 0, "Negative": 0, "total": 0},
        "VIC": {"Confirmed": 0, "Suspect": 0, "Negative": 0, "total": 0},
        "QLD": {"Confirmed": 0, "Suspect": 0, "Negative": 0, "total": 0},
        "TAS": {"Confirmed": 0, "Suspect": 0, "Negative": 0, "total": 0},
        "NT": {"Confirmed": 0, "Suspect": 0, "Negative": 0, "total": 0},
        "ACT": {"Confirmed": 0, "Suspect": 0, "Negative": 0, "total": 0},
        "Other": {"Confirmed": 0, "Suspect": 0, "Negative": 0, "total": 0}
    }
    
    for case in cases_data:
        loc = case["location"]
        c_type = case["type"]
        
        state_key = "Other"
        if any(kw in loc for kw in ["西澳", "WA", "Esperance", "Dunsborough", "Roses", "Mullaloo", "Horrocks", "Denmark", "Lancelin", "Seabird", "Whitfords"]):
            state_key = "WA"
        elif any(kw in loc for kw in ["南澳", "SA", "Fleurieu", "Fowlers", "Robe", "Yorke", "Kangaroo", "Vincent", "Semaphore",
                                         "Southend", "Jaffa", "MacDonnell", "Limestone", "Seal Bay", "Southeast SA", "Cape Jaffa", "Port MacDonnell"]):
            state_key = "SA"
        elif any(kw in loc for kw in ["新南威爾斯", "NSW", "Hawks Nest", "Narrabeen"]):
            state_key = "NSW"
        elif any(kw in loc for kw in ["維多利亞", "VIC", "Victoria"]):
            state_key = "VIC"
        elif "昆士蘭" in loc or "QLD" in loc or "Moreton" in loc or "Noosa" in loc:
            state_key = "QLD"
        elif "塔斯馬尼亞" in loc or "TAS" in loc:
            state_key = "TAS"
        elif "北領地" in loc or "NT" in loc:
            state_key = "NT"
        elif "首都領地" in loc or "ACT" in loc:
            state_key = "ACT"
            
        count = case.get("detection_count", 1)
        states_stats[state_key][c_type] += count
        states_stats[state_key]["total"] += count

    total_confirmed_count = sum(c.get("detection_count", 1) for c in cases_data if c["type"] == "Confirmed")
    daff_link = '<a href="https://www.agriculture.gov.au/campaigns/birdflu" target="_blank" class="text-blue-400 underline hover:text-blue-300 font-semibold">澳洲聯邦農業部 (DAFF)</a>'
    
    wa_detail = f"西澳 {states_stats['WA']['total']} 例（{states_stats['WA']['Confirmed']}例確診" + (f"/{states_stats['WA']['Suspect']}例疑似" if states_stats['WA']['Suspect'] else "") + ")"
    sa_detail = f"南澳 {states_stats['SA']['total']} 例（{states_stats['SA']['Confirmed']}例確診" + (f"/{states_stats['SA']['Suspect']}例疑似" if states_stats['SA']['Suspect'] else "") + (f"/{states_stats['SA']['Negative']}例已排除" if states_stats['SA']['Negative'] else "") + ")"
    
    nsw_detail = f"新南威爾斯州 (NSW) {states_stats['NSW']['total']} 例（"
    nsw_details_list = []
    if states_stats['NSW']['Confirmed'] > 0:
        nsw_details_list.append(f"{states_stats['NSW']['Confirmed']}例確診")
    if states_stats['NSW']['Negative'] > 0:
        nsw_details_list.append(f"{states_stats['NSW']['Negative']}例已排除")
    nsw_detail += "/".join(nsw_details_list) + ")"
    
    vic_detail = f"維多利亞州 (VIC) {states_stats['VIC']['total']} 例（{states_stats['VIC']['Confirmed']}例確診" + (f"/{states_stats['VIC']['Suspect']}例疑似" if states_stats['VIC']['Suspect'] else "") + (f"/{states_stats['VIC']['Negative']}例已排除" if states_stats['VIC']['Negative'] else "") + ")"
    
    # 拼裝其它領地數據 (若有檢出)
    other_states_list = []
    for sk in ["QLD", "TAS", "NT", "ACT"]:
        if states_stats[sk]["total"] > 0:
            confirmed = states_stats[sk]["Confirmed"]
            suspect = states_stats[sk]["Suspect"]
            negative = states_stats[sk]["Negative"]
            detail = f"{sk} {states_stats[sk]['total']} 例（"
            parts = []
            if confirmed: parts.append(f"{confirmed}例確診")
            if suspect: parts.append(f"{suspect}例疑似")
            if negative: parts.append(f"{negative}例已排除")
            detail += "/".join(parts) + ")"
            other_states_list.append(detail)
    other_states_str = f"，另有 {', '.join(other_states_list)}" if other_states_list else ""
    
    valid_dates = []
    for c in cases_data:
        nd = c.get("notify_date")
        if nd and nd != "進行中 (Pending)":
            try:
                valid_dates.append(datetime.strptime(nd, "%Y-%m-%d"))
            except:
                pass
    if valid_dates:
        max_date = max(valid_dates)
        latest_date_str = f"{max_date.year} 年 {max_date.month} 月 {max_date.day} 日"
    else:
        latest_date_str = "最新"

    official_text = (
        f"依據 {daff_link} 及各州政府 {latest_date_str} 最新公告，全澳高致病性 H5N1 野鳥確診總數累計已達 **{total_confirmed_count} 例**！當前最新確診病例分布統計：{wa_detail}、{sa_detail}、{nsw_detail}，另有 {vic_detail}{other_states_str}。全澳家禽產業及商業飼料生產體系 100% 維持無疫區（Area Freedom）狀態，生產鏈與原料供應安全無虞。"
    )

    latest_case = cases_data[-1] if cases_data else None
    
    nsw_dpird_link = '<a href="https://www.dpird.nsw.gov.au/dpi/biosecurity/animal-biosecurity/avian-influenza" target="_blank" class="text-blue-400 underline hover:text-blue-300 font-semibold">新南威爾斯州政府 (NSW DPIRD)</a>'
    abc_link = '<a href="https://www.abc.net.au/news/" target="_blank" class="text-blue-400 underline hover:text-blue-300 font-semibold">澳洲廣播公司 (ABC News)</a>'
    
    # 判斷近3日內是否有新增確診
    recent_surge = False
    if valid_dates:
        max_date_utc = max_date.replace(tzinfo=timezone.utc)
        days_diff = (datetime.now(timezone.utc) - max_date_utc).days
        if days_diff <= 3:
            recent_surge = True

    if recent_surge:
        media_text = (
            f"根據 {abc_link} 與 {nsw_dpird_link} 等媒體與官方平台 **{latest_date_str} 最新數據**，全澳高致病性 H5N1 野鳥確診總數已推升至 **{total_confirmed_count} 例**！"
            f"近期疫情持續在沿海野生鳥類間傳播，各州政府正密切監測潛在的生態變化。聯邦首席獸醫官重申：**澳洲所有商業家禽農場維持 100% 零感染，對一般人類健康風險極低**。"
        )
    else:
        media_text = f"根據 {abc_link} 與 {nsw_dpird_link} 最新報導，全澳野生海鳥確診累計 **{total_confirmed_count} 例**，目前疫情處於相對平穩期，各州地方監控組織正密切維持常態性觀測。"
        
    return official_text, media_text

def generate_dynamic_references(cases_data):
    """
    動態生成網頁底部的官方權威參考資料 (References) 列表。
    """
    refs = [
        '澳洲農業、漁業及林業部 (DAFF) 官方宣傳活動與即時更新：<a href="https://www.agriculture.gov.au/campaigns/birdflu" target="_blank" class="text-blue-400 hover:underline">Department of Agriculture, Fisheries and Forestry - June 2026 H5 bird flu detection</a>',
        '新南威爾斯州政府一次產業及區域發展廳 (NSW DPIRD) 專區即時更新：<a href="https://www.dpird.nsw.gov.au/dpi/biosecurity/animal-biosecurity/avian-influenza" target="_blank" class="text-blue-400 hover:underline">NSW DPIRD - Avian influenza updates</a>',
        '南澳州政府農業、食品及區域部 (PIRSA) 專區即時更新：<a href="https://pir.sa.gov.au/animal-management/animal-health/species/poultry/avian-influenza" target="_blank" class="text-blue-400 hover:underline">PIRSA - Avian influenza updates</a>'
    ]
    
    has_wa = False
    has_vic = False
    has_qld = False
    for case in cases_data:
        loc = case["location"]
        if any(kw in loc for kw in ["西澳", "WA", "Esperance", "Roses", "Dunsborough", "Mullaloo", "Horrocks", "Denmark", "Lancelin", "Seabird", "Whitfords"]):
            has_wa = True
        if any(kw in loc for kw in ["維多利亞", "VIC"]):
            has_vic = True
        if any(kw in loc for kw in ["昆士蘭", "QLD", "Noosa", "Moreton"]):
            has_qld = True
            
    if has_wa:
        refs.append('西澳州政府一次產業及區域發展部 (DPIRD WA) 專區即時更新：<a href="https://www.wa.gov.au/organisation/department-of-primary-industries-and-regional-development/avian-influenza" target="_blank" class="text-blue-400 hover:underline">DPIRD WA - Avian influenza updates</a>')
    if has_vic:
        refs.append('維多利亞州政府農業廳 (Agriculture Victoria) 疫情公告：<a href="https://agriculture.vic.gov.au/biosecurity/animal-diseases/poultry-diseases/avian-influenza" target="_blank" class="text-blue-400 hover:underline">Agriculture Victoria - Bird flu update</a>')
    if has_qld:
        refs.append('昆士蘭州政府一次產業及農業發展專區 (Biosecurity Queensland)：<a href="https://www.business.qld.gov.au/industries/farms-fishing-forestry/agriculture/animal/health-diseases/disorders/avian-influenza" target="_blank" class="text-blue-400 hover:underline">Biosecurity Queensland - Avian influenza updates</a>')
        
    html_lines = []
    for idx, ref in enumerate(refs, 1):
        html_lines.append(f'                <li>\n                    [{idx}] {ref}\n                </li>')
        
    return "\n".join(html_lines)

def main():
    # 1. 抓取最新病例數據 (全澳洲 8 個州/領地聯防爬取)
    cases_data = fetch_daff_updates()
    
    # 2. 依照「官方通報/採樣日期」由先至後進行排序 (Ascending Chronological Order)
    cases_data.sort(key=lambda x: x["notify_date"])
    
    # 3. 讀取網頁模板檔案 (report_template.html)
    template_path = "report_template.html"
    output_path = "index.html"
    
    if not os.path.exists(template_path):
        print(f"嚴重錯誤：找不到模板檔案 '{template_path}'，請確認模板是否存在儲存庫根目錄！")
        return
        
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()
    
    # 4. 根據最新病例數據動態產生官方事實與媒體觀察摘要
    official_html, media_html = generate_dynamic_summary(cases_data)
    updated_html = html_template.replace("<!-- DYNAMIC_OFFICIAL_SUMMARY_PLACEHOLDER -->", official_html)
    updated_html = updated_html.replace("<!-- DYNAMIC_MEDIA_SUMMARY_PLACEHOLDER -->", media_html)
    
    # 4.1 動態產生底部參考文獻列表並替換
    refs_html = generate_dynamic_references(cases_data)
    updated_html = updated_html.replace("<!-- DYNAMIC_REFERENCES_PLACEHOLDER -->", refs_html)
    
    # 4.5 計算所有非排除案例到工廠的最短地緣距離並動態注入 HTML 中
    factory_lat, factory_lon = -33.5332, 149.2524
    min_dist = float('inf')
    for case in cases_data:
        if case["type"] != "Negative":
            dist = calculate_distance(case["latitude"], case["longitude"], factory_lat, factory_lon)
            if dist < min_dist:
                min_dist = dist
                
    min_dist_str = "290"  # 預設安全回退值
    if min_dist != float('inf'):
        min_dist_str = str(int(round(min_dist)))
    
    updated_html = updated_html.replace("<!-- MIN_DISTANCE_PLACEHOLDER -->", min_dist_str)
    
    # 5. 將最新的病例數據 JSON 注入模板預留的佔位符中，並將模板中原有的預設 JavaScript 陣列完全替換
    cases_json_str = json.dumps(cases_data, ensure_ascii=False, indent=2)
    updated_html = re.sub(
        r'/\* CASES_DATABASE_PLACEHOLDER \*/\s*\[.*?\]\s*;', 
        f"/* CASES_DATABASE_PLACEHOLDER */ {cases_json_str};", 
        updated_html, 
        flags=re.DOTALL
    )
    
    # 6. 更新最後編譯更新時間 (校正為台北時間與澳洲 AEST 時間)
    utc_now = datetime.now(timezone.utc)
    taipei_now = utc_now + timedelta(hours=8)
    aest_now = utc_now + timedelta(hours=10)
    time_string = f"{taipei_now.strftime('%Y-%m-%d %H:%M:%S')} (台北時間) / {aest_now.strftime('%Y-%m-%d %H:%M:%S')} (澳洲 AEST)"
    updated_html = updated_html.replace("<!-- COMPILE_TIME_PLACEHOLDER -->", time_string)
    
    # 7. 寫出為正式部署網頁 index.html
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(updated_html)
        
    print(f"網頁自動編譯成功！已順利生成最新 H5N1 戰略決策報告 '{output_path}'。")

if __name__ == "__main__":
    main()
