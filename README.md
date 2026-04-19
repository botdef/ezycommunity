# EzyCommunity

แอปจัดการงาน เตือนงาน นัดประชุม และเร่งด่วน — รันหลักด้วย [Streamlit](https://streamlit.io) เชื่อม [Supabase](https://supabase.com) ได้  
ในรีโปมีโปรโตไทป์ **Next.js** (`app/`, `npm run dev`) แยกจากแอป Streamlit — ไม่บังคับสำหรับ deploy

## ความต้องการของระบบ

- Python **3.11** (แนะนำให้ตรงกับ `runtime.txt` สำหรับ Streamlit Community Cloud)
- Node 18+ (เฉพาะเมื่อจะรัน / build โปรเจกต์ Next.js ในรีโป)

## รันแอปหลัก (Streamlit)

```bash
cd <โฟลเดอร์หลัง-clone-repo>
python -m pip install -r requirements.txt
# Windows: copy .env.example .env   |  macOS/Linux: cp .env.example .env
# แก้ .env ใส่ SUPABASE_URL / SUPABASE_KEY ถ้าใช้ฐานข้อมูล
python -m streamlit run app.py
```

เปิดเบราว์เซอร์ที่ `http://localhost:8501`  
ทางเลือก: `python -m streamlit run app/main.py` (สคริปต์ชี้ไปที่ `app.py` ที่ root)

## ฐานข้อมูล Supabase

1. สร้างโปรเจกต์ใน Supabase  
2. ที่ **SQL Editor** รันไฟล์ **`supabase/schema.sql`** ทั้งไฟล์  
3. คัดลอก **Project URL** และ **anon key** (หรือ service role สำหรับทดสอบส่วนตัว) ไปใส่ `.env` หรือ Secrets บน Cloud  

ตาราง: `tasks`, `notes`, `settings` — ฟิลด์ให้ตรงกับสคีมาในไฟล์ SQL (แอป insert/update ตาม `database.py`)

## ตัวแปรสภาพแวดล้อม (`.env`)

| ตัวแปร | คำอธิบาย |
|--------|----------|
| `SUPABASE_URL` / `SUPABASE_KEY` | เชื่อมฐานข้อมูล (ไม่ใส่ = โหมดตัวอย่างในเซสชัน) |
| `ENABLE_GOOGLE_CALENDAR` | `true` เมื่อพร้อมใช้ Google Calendar (ค่าเริ่มต้นปิด) |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `GOOGLE_REDIRECT_URI` | OAuth สำหรับ Calendar |
| `GEMINI_API_KEY` หรือ `GOOGLE_API_KEY` | หน้า AI วางแผน (Gemini) |
| `GEMINI_MODEL` | เช่น `gemini-2.0-flash` — ไม่บังคับ |

อย่า commit ไฟล์ `.env` — อยู่ใน `.gitignore` แล้ว

## เชื่อม Supabase แบบพิมพ์ในแอป

ที่แถบข้างมีปุ่ม **เชื่อม Supabase (พิมพ์เอง)** — เก็บ URL/คีย์ใน **session เท่านั้น** (รีเฟรชหน้าจะหาย) เหมาะทดสอมบน Cloud โดยไม่ตั้ง Secrets ทันที  
ถ้าต้องการถาวรบน Streamlit Cloud ให้ใช้ **Secrets** ตามด้านล่าง

## Deploy บน Streamlit Community Cloud

1. Push โค้ดขึ้น GitHub  
2. ที่ [share.streamlit.io](https://share.streamlit.io) สร้างแอป ชี้ที่ **`app.py`**  
3. **Secrets** ใส่ค่าแบบ TOML ชื่อ **flat** (แอปจะคัดลอกไป `os.environ` ให้)

```toml
SUPABASE_URL = "https://....supabase.co"
SUPABASE_KEY = "...."
```

ห้ามพึ่งแค่ nested อย่าง `[connections.supabase]` อย่างเดียวถ้าไม่มีคีย์ flat ด้านบน — แอปจะไม่อ่านค่า

## ฟีเจอร์หลักใน `app.py` (สรุป)

- แดชบอร์ด / งาน (เพิ่มงานจริง, ลบแบบยืนยัน, ค้นหา/กรอง, ส่งออกงานเสร็จ HTML+CSV สำหรับพิมพ์)  
- เร่งด่วน, นัดประชุม, ปฏิทิน, AI วางแผน, บันทึก, ตั้งค่า  
- รายละเอียดงานแยกช่อง «คำสั่ง / หมายเหตุ» รวมในฟิลด์ `description` ในฐานข้อมูล (มีตัวคั่นข้อความในโค้ด)

## โปรเจกต์ Next.js (ทางเลือก)

```bash
npm install
npm run dev
```

```bash
npm run build
```

ใช้สำหรับ UI ทดลองแยกจาก Streamlit — **ไม่ใช่** entrypoint ที่ Cloud รันโดยค่าเริ่มต้น

## ก่อน push ขึ้น GitHub (เช็กลิสต์)

- [ ] ไม่มี `.env` หรือคีย์จริงใน commit (`git status` / `git diff`)  
- [ ] รัน `python -m py_compile app.py database.py google_calendar.py` ผ่าน  
- [ ] รัน `streamlit run app.py` ลองเพิ่ม/ลบงานกับ Supabase จริง  
- [ ] (ถ้ามี Next ใน CI) `npm run build` ผ่าน  
- [ ] อัปเดต `README.md` / `requirements.txt` แล้วถ้ามี dependency ใหม่  

## คำสั่ง Git

```bash
git add .
git status
git commit -m "ข้อความสรุปการเปลี่ยนแปลง"
git push origin main
```

## โครงสร้างสำคัญ

| ไฟล์ / โฟลเดอร์ | คำอธิบาย |
|------------------|----------|
| `app.py` | แอป Streamlit หลัก |
| `database.py` | คลาส `DBManager` เชื่อม Supabase |
| `google_calendar.py` | Google Calendar (เปิดด้วย env ที่เกี่ยวข้อง) |
| `supabase/schema.sql` | SQL สร้างตาราง + RLS เบื้องต้น |
| `runtime.txt` | เวอร์ชัน Python บน Streamlit Cloud |
| `app/` (Next) | โปรโตไทป์ UI แยก |

## หมายเหตุ

- **Google Calendar** และ **Gemini** เป็นทางเลือก — ตั้งเมื่อพร้อม  
- สคีมาใน `schema.sql` ใช้ policy แบบเปิดกว้างสำหรับ `anon` — ก่อนขึ้น production ควรจำกัดสิทธิ์ตามบัญชีผู้ใช้
