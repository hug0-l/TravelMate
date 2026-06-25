"""Tokyo 5-Day Trip Seed — fixed password + auth."""
import httpx, json, sys

BASE = "http://127.0.0.1:8001"
c = httpx.Client(base_url=BASE, timeout=10)

def log(method, path, status):
    print(f"  {method:6s} {path:50s} {status}")
    sys.stdout.flush()

# 1. Register (password >= 8 chars)
print("=== 1. Register ===")
r = c.post("/api/auth/register", json={"email":"tokyo@test.com","name":"飄兒","password":"test1234"})
log("POST", "/api/auth/register", r.status_code)
data = r.json()
token = data["access_token"]
uid = data["user_id"]
print(f"   Token: {token[:30]}...")
print(f"   UserID: {uid}")

c.headers["Authorization"] = f"Bearer {token}"

# 2. Trip
print("\n=== 2. Trip ===")
r = c.post("/api/trips/", json={
    "title": "🇯🇵 東京五天四夜自由行 — 新手經典路線",
    "start_date": "2026-10-01", "end_date": "2026-10-05", "duration_days": 5,
    "origin_country": "台灣","destination_country": "日本","destination_tz_offset": 9,"visibility": "shared",
})
log("POST", "/api/trips/", r.status_code)
trip = r.json()
tid = trip["id"]
print(f"   Trip ID: {tid}")

# 3. Days
print("\n=== 3. Days ===")
days = {}
for dt, title in [
    ("2026-10-01","Day 1 🛫 抵達×澀谷×新宿"),
    ("2026-10-02","Day 2 🗻 河口湖一日遊"),
    ("2026-10-03","Day 3 ⛩️ 淺草×上野×晴空塔"),
    ("2026-10-04","Day 4 🌊 鎌倉江之島"),
    ("2026-10-05","Day 5 🛬 東京車站×回國"),
]:
    r = c.post(f"/api/trips/{tid}/days", json={"date": dt, "title": title})
    days[dt] = r.json()["id"]
    log("POST", f"/api/trips/{tid}/days [{dt}]", r.status_code)

# 4. Activities
print("\n=== 4. Activities ===")
acts = [
    ("2026-10-01","✈️ 桃園→成田","transport","06:00","10:00"),
    ("2026-10-01","🚄 N'EX→新宿","transport","10:30","12:00"),
    ("2026-10-01","🏨 飯店Check-in","accommodation","12:00","13:00"),
    ("2026-10-01","🍜 麵屋海神午餐","food","13:00","14:00"),
    ("2026-10-01","🛍️ 澀谷＋SHIBUYA SKY","attraction","14:30","17:00"),
    ("2026-10-01","🥩 牛かつもと村","food","17:30","18:30"),
    ("2026-10-01","🌃 新宿夜遊","attraction","19:00","21:00"),
    ("2026-10-02","🚌 新宿→河口湖","transport","07:30","10:00"),
    ("2026-10-02","🗻 天上山公園","attraction","10:00","11:30"),
    ("2026-10-02","🚢 河口湖遊覽船","attraction","11:30","12:30"),
    ("2026-10-02","🍜 ほうとう不動","food","12:30","13:30"),
    ("2026-10-02","📸 大石公園","attraction","13:30","15:30"),
    ("2026-10-02","🛍️ 河口湖伴手禮","shopping","15:30","16:30"),
    ("2026-10-02","🚌 河口湖→新宿","transport","17:00","19:00"),
    ("2026-10-02","🍣 蟹道樂晚餐","food","19:30","21:00"),
    ("2026-10-03","🚇 新宿→淺草","transport","09:00","09:45"),
    ("2026-10-03","⛩️ 淺草寺＋仲見世","attraction","10:00","12:00"),
    ("2026-10-03","🍡 大黑家天麩羅","food","12:00","13:00"),
    ("2026-10-03","🌳 上野恩賜公園","attraction","13:30","15:00"),
    ("2026-10-03","🛍️ 阿美橫丁","shopping","15:00","17:00"),
    ("2026-10-03","🗼 晴空塔夜景","attraction","17:30","19:00"),
    ("2026-10-03","🍜 六厘舍沾麵","food","19:00","20:00"),
    ("2026-10-04","🚄 新宿→鎌倉","transport","08:00","09:00"),
    ("2026-10-04","☕ 鎌倉早餐","food","09:00","10:00"),
    ("2026-10-04","⛩️ 鶴岡八幡宮","attraction","10:00","11:00"),
    ("2026-10-04","🚃 江之電","transport","11:00","11:20"),
    ("2026-10-04","🗿 鎌倉大佛","attraction","11:30","12:00"),
    ("2026-10-04","🍱 鎌倉午餐","food","12:00","13:00"),
    ("2026-10-04","🌊 鎌倉高校前","attraction","13:00","14:00"),
    ("2026-10-04","🏝️ 江之島","attraction","14:30","17:00"),
    ("2026-10-04","🚄 鎌倉→新宿","transport","17:30","18:30"),
    ("2026-10-04","🥩 六歌仙燒肉","food","19:00","20:30"),
    ("2026-10-05","🏨 退房","accommodation","08:00","09:00"),
    ("2026-10-05","🗼 東京車站一番街","shopping","09:00","11:00"),
    ("2026-10-05","🍰 HARBS蛋糕","food","11:00","11:30"),
    ("2026-10-05","🚄 東京→成田","transport","12:00","13:30"),
    ("2026-10-05","🛍️ 成田機場採購","shopping","13:30","15:00"),
    ("2026-10-05","✈️ 成田→桃園","transport","16:00","19:00"),
]
for dt, title, cat, st, et in acts:
    r = c.post(f"/api/days/{days[dt]}/activities", json={
        "title": title, "category": cat, "start_time": st, "end_time": et,
    })
    if r.status_code >= 400:
        log("ERR", f"/api/days/{days[dt]}/activities [{title}]", r.status_code)

# 5. Expenses
print("\n=== 5. Expenses ===")
total = 0
for title, amt, cat in [
    ("機票來回",15000,"transport"),("新宿4晚住宿",32000,"accommodation"),
    ("河口湖巴士來回",4400,"transport"),("SHIBUYA SKY",2200,"activity"),
    ("晴空塔",2100,"activity"),("纜車+遊覽船",2100,"activity"),
    ("鎌倉大佛",300,"activity"),("牛かつもと村",1500,"food"),
    ("麵屋海神",1200,"food"),("ほうとう不動",1200,"food"),
    ("六厘舍",1000,"food"),("六歌仙",6500,"food"),
    ("蟹道樂",6000,"food"),("大黑家",2000,"food"),
    ("藥妝採購",8000,"shopping"),("伴手禮",2400,"shopping"),
    ("Suica交通",5000,"transport"),("地鐵24小時券",800,"transport"),
    ("其他雜支",5000,"other"),
]:
    r = c.post(f"/api/trips/{tid}/expenses", json={
        "title": title, "amount": amt, "category": cat, "paid_by": uid, 
    })
    total += amt
print(f"   Total budget: ¥{total:,}")

# 6. Memories
print("\n=== 6. Memories ===")
for title, content in [
    ("🌸 初抵東京！澀谷的震撼","從成田搭N'EX到新宿，澀谷十字路口好震撼！SHIBUYA SKY夜景美到窒息，牛かつもと村的炸牛排外酥內嫩！"),
    ("🗻 富士山出現了","河口湖晴空萬里，富士山雪白發亮。天上山纜車拍到了人生照片！"),
    ("⛩️ 淺草寺穿越時空","穿和服走在淺草寺參道超有感覺！仲見世通人形燒熱騰騰。"),
    ("🌊 鎌倉青春電車","站在鎌倉高校前平交道，江之電噹噹駛過，灌籃高手回憶湧上。"),
    ("✈️ 五天太短了","東京車站一番街掃貨，成田銀座篝雞白湯拉麵讓人再次感動！🇯🇵"),
]:
    c.post(f"/api/trips/{tid}/memories", json={"title":title,"content":content,"date":"2026-10-05"})

# 7. POIs
print("\n=== 7. POIs ===")
for name, cat, addr, lat, lng in [
    ("SHIBUYA SKY","attraction","澀谷",35.6595,139.7004),
    ("淺草寺（雷門）","attraction","台東區淺草",35.7148,139.7967),
    ("東京晴空塔","attraction","墨田區押上",35.7101,139.8107),
    ("上野恩賜公園","attraction","台東區上野公園",35.7147,139.7733),
    ("阿美橫丁","shopping","台東區上野",35.7134,139.7745),
    ("鎌倉大佛","attraction","鎌倉市長谷",35.3168,139.5201),
    ("鶴岡八幡宮","attraction","鎌倉市雪之下",35.3268,139.5597),
    ("鎌倉高校前","attraction","鎌倉市腰越",35.3065,139.4959),
    ("江之島","attraction","藤澤市",35.2995,139.4798),
    ("河口湖天上山","attraction","富士河口湖町",35.5143,138.7716),
    ("東京車站一番街","shopping","千代田區",35.6812,139.7671),
]:
    c.post(f"/api/trips/{tid}/pois", json={"name":name,"category":cat,"address":addr,"lat":lat,"lng":lng})

# 8. Packing
print("\n=== 8. Packing ===")
for name, cat in [
    ("護照","document"),("錢包/日幣","document"),
    ("充電器","electronics"),("行動電源","electronics"),
    ("eSIM","electronics"),("牙刷","toiletries"),
    ("衣物x3","clothing"),("外套","clothing"),
    ("步行鞋","clothing"),("雨傘","other"),
    ("藥品","medicine"),("相機","electronics"),("購物袋","other"),
]:
    c.post(f"/api/trips/{tid}/packing", json={"name":name,"category":cat,"quantity":1})

# 9. Budget summary
print("\n=== 9. Budget Summary ===")
r = c.get(f"/api/trips/{tid}/budget-summary")
bs = r.json()
print(f"   Total: ¥{bs['total_expenses']:,.0f}")

print(f"\n✅ DONE!")
print(f"   Login: tokyo@test.com / test1234")
print(f"   Trip ID: {tid}")
