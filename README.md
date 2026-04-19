# EzyCommunity

แอปจัดการงาน ปฏิทิน บันทึก และ AI ช่วยวางแผน — รันด้วย [Streamlit](https://streamlit.io) เชื่อม [Supabase](https://supabase.com) ได้

## ความต้องการของระบบ

- Python 3.10+ (แนะนำ 3.11+)

## รันในเครื่อง

```bash
cd ezycommunity
python -m pip install -r requirements.txt
copy .env.example .env
# แก้ไข .env ใส่ SUPABASE_URL / SUPABASE_KEY ถ้าใช้ฐานข้อมูล
python -m streamlit run app.py
```

เปิดเบราว์เซอร์ที่ `http://localhost:8501`

## ตัวแปรสภาพแวดล้อม (`.env`)

| ตัวแปร | คำอธิบาย |
|--------|----------|
| `SUPABASE_URL` / `SUPABASE_KEY` | เชื่อมฐานข้อมูล (ไม่ใส่ = โหมดตัวอย่างในเซสชัน) |
| `ENABLE_GOOGLE_CALENDAR` | `true` เมื่อพร้อมเชื่อม Google Calendar (ค่าเริ่มต้นปิด) |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `GOOGLE_REDIRECT_URI` | OAuth สำหรับ Calendar (ใช้เมื่อเปิดด้านบน) |
| `GEMINI_API_KEY` หรือ `GOOGLE_API_KEY` | ใช้ Gemini ในหน้า AI วางแผน |
| `GEMINI_MODEL` | รุ่นโมเดล (เช่น `gemini-2.0-flash`) — ไม่บังคับ |

อย่า commit ไฟล์ `.env` — โปรเจกต์ ignore ไว้แล้ว

## Deploy บน Streamlit Community Cloud

1. Push โค้ดขึ้น GitHub (repo แบบ public หรือตามแพลนที่ใช้)
2. ที่ [share.streamlit.io](https://share.streamlit.io) สร้างแอป ชี้ที่ **`app.py`**
3. ใน **Secrets** ใส่ค่าเดียวกับ `.env` (รูปแบบ TOML)

```toml
SUPABASE_URL = "https://....supabase.co"
SUPABASE_KEY = "...."
```

## ขึ้น GitHub

```bash
git add .
git commit -m "Describe your change"
git push origin main
```

## โครงสร้างสำคัญ

- `app.py` — แอปหลัก Streamlit
- `database.py` — คลาสเชื่อม Supabase
- `google_calendar.py` — Google Calendar (เปิดด้วย `ENABLE_GOOGLE_CALENDAR=true`)

## หมายเหตุ

- การเชื่อม **Google Calendar** เป็นทางเลือก — ตั้งค่าเมื่อพร้อมตามตารางด้านบน
- ตาราง `tasks` / `notes` / `settings` ใน Supabase ต้องสอดคล้องกับฟิลด์ที่แอปใช้
