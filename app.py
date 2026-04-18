import os
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

import streamlit as st
from dotenv import load_dotenv

from database import DBManager

load_dotenv()

st.set_page_config(
    page_title="EzyCommunity",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)


@dataclass
class Task:
    title: str
    description: str
    due_date: str
    priority: str
    status: str
    tag: str


MOCK_TASKS: List[Task] = [
    Task("เตรียมรายงานประจำสัปดาห์", "สรุปความคืบหน้าและความเสี่ยงที่อาจเกิดขึ้น", "2026-04-19", "สูง", "เกินกำหนด", "งาน"),
    Task("จดบันทึกการประชุมทีม", "รวบรวมมติและรายการงานที่ต้องดำเนินการ", "2026-04-19", "ปานกลาง", "กำลังทำ", "งานแอดมิน"),
    Task("ตรวจสอบการเชื่อมปฏิทิน", "เช็กว่างานถูกผูกกับปฏิทินหรือยัง", "2026-04-20", "ต่ำ", "เสร็จแล้ว", "ระบบ"),
    Task("วางแผนประชาสัมพันธ์ชุมชน", "ร่างไทม์ไลน์กิจกรรมสำหรับสัปดาห์หน้า", "2026-04-21", "เร่งด่วน", "ต้องทำ", "ชุมชน"),
    Task("เตรียมข้อเสนอโปรเจกต์", "ร่าง outline และนำเสนอให้ทีมตรวจทาน", "2026-04-22", "สูง", "ต้องทำ", "Planning"),
    Task("รอข้อมูลจากลูกค้า", "รอไฟล์และคำตอบจากฝั่งลูกค้า", "2026-04-23", "ต่ำ", "รออยู่", "Waiting"),
]

NAV_ITEMS = ["แดชบอร์ด", "งาน", "ปฏิทิน", "AI วางแผน", "บันทึก", "ตั้งค่า"]
STATUS_FLOW = ["ยังไม่ได้เริ่ม", "กำลังทำ", "รออยู่", "เกินกำหนด", "เสร็จแล้ว"]


st.markdown(
    """
    <style>
      .block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1280px; }
      .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%);
        color: white; padding: 1.6rem 1.8rem; border-radius: 24px; margin-bottom: 1rem;
        box-shadow: 0 12px 32px rgba(15, 23, 42, 0.18);
      }
      .card {
        background: white; border: 1px solid #e5e7eb; border-radius: 18px;
        padding: 1rem 1.1rem; box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
      }
      .card-title { color: #0f172a; font-size: 0.92rem; font-weight: 600; letter-spacing: .02em; }
      .muted { color: #64748b; font-size: 0.92rem; }
      .pill {
        display:inline-block; padding: .25rem .65rem; border-radius: 999px; font-size: .78rem;
        background: #e2e8f0; color: #0f172a; margin-right: .35rem;
      }
      .metric {
        background: white; border: 1px solid #e5e7eb; border-radius: 18px; padding: 1rem 1.1rem;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
      }
      .task-row {
        background: white; border: 1px solid #e5e7eb; border-radius: 16px; padding: .95rem 1rem;
        margin-bottom: .75rem;
      }
      .sidebar-brand { font-size: 1.2rem; font-weight: 800; color: #0f172a; }
      .small { font-size: .84rem; }
      .status-badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
      }
      .status-todo { background: #e2e8f0; color: #0f172a; }
      .status-progress { background: #dbeafe; color: #1d4ed8; }
      .status-waiting { background: #fef3c7; color: #b45309; }
      .status-overdue { background: #fee2e2; color: #b91c1c; }
      .status-done { background: #dcfce7; color: #166534; }
      .kanban-col {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 22px;
        padding: 1rem;
        min-height: 240px;
      }
      .kanban-header {
        display:flex; justify-content:space-between; align-items:center; gap:1rem;
        margin-bottom: .9rem;
      }
      .kanban-title { font-size: .95rem; font-weight: 700; color: #0f172a; }
      .kanban-count {
        min-width: 2rem; height: 2rem; border-radius: 999px; display:flex; align-items:center; justify-content:center;
        background: white; border: 1px solid #dbeafe; color: #2563eb; font-size: .8rem; font-weight: 700;
      }
      .kanban-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: .95rem 1rem;
        box-shadow: 0 6px 18px rgba(15,23,42,.05);
        margin-bottom: .75rem;
      }
      .kanban-card:hover { border-color: #bfdbfe; box-shadow: 0 10px 24px rgba(37,99,235,.08); }
      div[data-baseweb="select"] > div {
        border-radius: 14px;
        border-color: #dbeafe;
        background: #eff6ff;
      }
      div[data-baseweb="select"] span {
        color: #1d4ed8;
        font-weight: 600;
      }
      div[data-testid="stSelectbox"] { margin-top: .5rem; }
      .section-tab {
        display: inline-flex; align-items: center; gap: .5rem;
        padding: .65rem 1rem; border-radius: 999px; border: 1px solid #dbeafe;
        background: #eff6ff; color: #1d4ed8; font-weight: 700; font-size: .86rem;
      }
      .section-tab.active {
        background: #2563eb; color: white; border-color: #2563eb;
        box-shadow: 0 10px 20px rgba(37,99,235,.18);
      }
      .action-chip {
        display:inline-flex; align-items:center; gap:.4rem; padding:.45rem .75rem; border-radius:999px;
        border:1px solid #dbeafe; background:#eff6ff; color:#1d4ed8; font-size:.8rem; font-weight:700;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_db() -> Optional[DBManager]:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        return None
    try:
        return DBManager()
    except Exception:
        return None


def fetch_tasks(db: Optional[DBManager]):
    if db is None:
        return [task.__dict__ for task in MOCK_TASKS]
    try:
        result = db.fetch_tasks()
        if getattr(result, "data", None):
            return result.data
    except Exception:
        pass
    return [task.__dict__ for task in MOCK_TASKS]


def fetch_notes(db: Optional[DBManager]):
    if db is None:
        return st.session_state.get("notes_data", [])
    try:
        result = db.fetch_notes()
        if getattr(result, "data", None):
            return result.data
    except Exception:
        pass
    return st.session_state.get("notes_data", [])


def fetch_settings(db: Optional[DBManager]):
    if db is None:
        return st.session_state.get("settings_data", {"name": "", "email": "", "reminder": True, "ai_mode": "ปานกลาง"})
    try:
        result = db.fetch_settings()
        if getattr(result, "data", None):
            return result.data[0]
    except Exception:
        pass
    return st.session_state.get("settings_data", {"name": "", "email": "", "reminder": True, "ai_mode": "ปานกลาง"})


def task_badge(priority: str) -> str:
    colors = {"ต่ำ": "#94a3b8", "ปานกลาง": "#3b82f6", "สูง": "#f59e0b", "เร่งด่วน": "#ef4444"}
    return colors.get(priority, "#64748b")


def status_badge(status: str) -> str:
    colors = {"ต้องทำ": "status-todo", "กำลังทำ": "status-progress", "รออยู่": "status-waiting", "เสร็จแล้ว": "status-done", "เกินกำหนด": "status-overdue"}
    return colors.get(status, "status-todo")


def render_header(title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="hero">
          <div style="font-size:2rem; font-weight:800; margin-bottom:.25rem;">{title}</div>
          <div style="opacity:.92; font-size:1rem;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard(tasks):
    render_header("แดชบอร์ด", "ดูภาพรวมงานวันนี้ สรุปสั้น ๆ และงานที่กำลังจะถึง")
    total = len(tasks)
    due_today = sum(1 for t in tasks if t.get("due_date") == date.today().isoformat())
    in_progress = sum(1 for t in tasks if t.get("status") == "กำลังทำ")
    completed = sum(1 for t in tasks if t.get("status") == "เสร็จแล้ว")

    c1, c2, c3, c4 = st.columns(4)
    for col, label, value in [(c1, "งานทั้งหมด", total), (c2, "ครบกำหนดวันนี้", due_today), (c3, "กำลังทำ", in_progress), (c4, "เสร็จแล้ว", completed)]:
        col.markdown(f"<div class='metric'><div class='muted'>{label}</div><h2 style='margin:.2rem 0 0'>{value}</h2></div>", unsafe_allow_html=True)

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("<div class='card'><div class='card-title'>สรุปจาก AI</div><p class='muted' style='margin-top:.5rem;'>ควรโฟกัสงานเร่งด่วนก่อน แล้วค่อยจัดการงานตามกำหนด ใช้หน้า AI วางแผนเมื่ออยากได้แผนรายวันหรือรายสัปดาห์</p><div style='margin-top:.75rem;'><span class='pill'>เร่งด่วน</span><span class='pill'>วันนี้</span><span class='pill'>ปฏิทิน</span></div></div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='card'><div class='card-title'>ตารางวันนี้</div><div class='small' style='margin-top:.6rem;'>09:00 — ประชุมเช้า</div><div class='small'>11:00 — เขียนรายงาน</div><div class='small'>14:00 — คุยลูกค้า</div><div class='small'>16:00 — ตรวจสอบการเชื่อมปฏิทิน</div></div>", unsafe_allow_html=True)

    st.write("")
    st.subheader("งานที่กำลังจะถึง")
    for task in tasks[:4]:
        st.markdown(
            f"""
            <div class='task-row'>
              <div style='display:flex; justify-content:space-between; gap:1rem; align-items:center;'>
                <div>
                  <div style='font-weight:700;'>{task.get('title')}</div>
                  <div class='muted small'>{task.get('description', '')}</div>
                </div>
                <div style='text-align:right;'>
                  <div><span class='pill' style='background:{task_badge(task.get('priority', ''))}; color:white;'>{task.get('priority', '')}</span></div>
                  <div class='small muted' style='margin-top:.35rem;'>ครบกำหนด: {task.get('due_date', '-')}</div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _normalize_task_status(task):
    title = str(task.get('title', '')).strip()
    due_date = str(task.get('due_date', '')).strip()
    status = str(task.get('status', '')).strip()

    if status in {'เสร็จแล้ว', 'Done'}:
        return 'เสร็จแล้ว'
    if status in {'กำลังทำ', 'In Progress'}:
        return 'กำลังทำ'
    if status in {'รออยู่', 'Waiting'}:
        return 'รออยู่'
    if status in {'เกินกำหนด', 'Overdue'}:
        return 'เกินกำหนด'

    if due_date and due_date < date.today().isoformat() and status not in {'เสร็จแล้ว', 'Done'}:
        return 'เกินกำหนด'
    if title:
        return 'ต้องทำ'
    return 'ต้องทำ'


def _group_tasks_by_status(tasks):
    groups = {
        'เกินกำหนด': [],
        'ยังไม่ได้เริ่ม': [],
        'กำลังทำ': [],
        'รออยู่': [],
        'เสร็จแล้ว': [],
    }
    for task in tasks:
        status = _normalize_task_status(task)
        if status == 'ต้องทำ':
            groups['ยังไม่ได้เริ่ม'].append(task)
        else:
            groups.setdefault(status, []).append(task)
    return groups


def _render_task_card(task):
    return f"""
    <div class='kanban-card'>
      <div style='display:flex; justify-content:space-between; gap:1rem; align-items:flex-start;'>
        <div>
          <div style='font-weight:700; font-size:1rem; color:#0f172a;'>{task.get('title')}</div>
          <div class='muted small' style='margin-top:.25rem;'>ครบกำหนด: {task.get('due_date', '-')}</div>
          <div class='small' style='margin-top:.4rem; color:#475569;'>{task.get('description', '')}</div>
        </div>
        <div style='text-align:right; min-width:120px;'>
          <div><span class='pill' style='background:{task_badge(task.get('priority', ''))}; color:white;'>{task.get('priority', '')}</span></div>
          <div style='margin-top:.45rem;'><span class='status-badge {status_badge(_normalize_task_status(task))}'>{_normalize_task_status(task)}</span></div>
        </div>
      </div>
    </div>
    """


def render_tasks(tasks):
    st.session_state.setdefault("tasks_data", tasks)
    st.session_state.setdefault("show_add_task", False)
    tasks_data = st.session_state["tasks_data"]

    col_a, col_b = st.columns([1, 0.35])
    with col_a:
        render_header("งาน", "Kanban board แบบแยกตามสถานะ ทำให้เห็นงานทุกกล่องชัดเจน")
    with col_b:
        if st.button("+ เพิ่มงาน", use_container_width=True):
            st.session_state["show_add_task"] = True

    if st.session_state.get("show_add_task"):
        with st.expander("เพิ่มงานใหม่", expanded=True):
            with st.form("add_task_form", clear_on_submit=True):
                title = st.text_input("ชื่องาน")
                description = st.text_area("รายละเอียด")
                col1, col2, col3 = st.columns(3)
                with col1:
                    due_date = st.date_input("กำหนดส่ง", value=date.today())
                with col2:
                    priority = st.selectbox("ความสำคัญ", ["ต่ำ", "ปานกลาง", "สูง", "เร่งด่วน"])
                with col3:
                    tag = st.text_input("แท็ก", value="งาน")
                status = st.selectbox("สถานะ", STATUS_FLOW, index=0)
                submitted = st.form_submit_button("บันทึกงาน", use_container_width=True)
                if submitted:
                    if not title.strip():
                        st.error("กรุณาใส่ชื่องาน")
                    else:
                        new_task = {
                            "title": title.strip(),
                            "description": description.strip(),
                            "due_date": due_date.isoformat(),
                            "priority": priority,
                            "status": status,
                            "tag": tag.strip() or "งาน",
                        }
                        if st.session_state.get("db") is not None:
                            try:
                                st.session_state["db"].insert_task(new_task)
                            except Exception as e:
                                st.error(f"บันทึกลงฐานข้อมูลไม่สำเร็จ: {e}")
                                st.stop()
                        tasks_data.append(new_task)
                        st.session_state["tasks_data"] = tasks_data
                        st.session_state["show_add_task"] = False
                        st.success("เพิ่มงานเรียบร้อยแล้ว")
                        st.rerun()

    f1, f2, f3, f4 = st.columns(4)
    f1.button("สถานะทั้งหมด", use_container_width=True)
    f2.button("ความสำคัญ", use_container_width=True)
    f3.button("แท็ก", use_container_width=True)
    f4.button("ค้นหา", use_container_width=True)

    groups = _group_tasks_by_status(tasks_data)
    status_order = [
        ('ยังไม่ได้เริ่ม', 'ยังไม่ได้เริ่ม'),
        ('กำลังทำ', 'กำลังทำ'),
        ('รออยู่', 'รออยู่'),
        ('เกินกำหนด', 'เกินกำหนด'),
        ('เสร็จแล้ว', 'เสร็จแล้ว'),
    ]

    st.markdown("<div style='margin:.5rem 0 1rem 0; color:#64748b; font-size:.92rem;'>งานทุกสถานะจะแสดงแยกเป็นกล่องด้านล่าง</div>", unsafe_allow_html=True)
    cols = st.columns(2)
    for index, (status_key, section_title) in enumerate(status_order):
        with cols[index % 2]:
            count = len(groups.get(status_key, []))
            st.markdown(
                f"<div class='kanban-col' style='margin-bottom:1rem;'><div class='kanban-header'><div><div class='kanban-title'>{section_title}</div><div class='muted small' style='margin-top:.2rem;'>{count} งาน</div></div><div class='kanban-count'>{count}</div></div></div>",
                unsafe_allow_html=True,
            )
            if count == 0:
                st.markdown("<div class='kanban-card'><div class='muted small'>ยังไม่มีงานในหมวดนี้</div></div>", unsafe_allow_html=True)
            else:
                for task in groups.get(status_key, []):
                    task_index = tasks_data.index(task)
                    st.markdown(_render_task_card(task), unsafe_allow_html=True)
                    current_status = _normalize_task_status(task)
                    current_status_index = STATUS_FLOW.index(current_status) if current_status in STATUS_FLOW else 0
                    new_status = st.selectbox(
                        f"เปลี่ยนสถานะของ {task.get('title')}",
                        STATUS_FLOW,
                        index=current_status_index,
                        key=f"status_select_{task_index}_{status_key}",
                        label_visibility="collapsed",
                    )
                    if new_status != current_status:
                        tasks_data[task_index]["status"] = new_status
                        st.session_state["tasks_data"] = tasks_data
                        st.rerun()


def render_calendar(tasks):
    render_header("ปฏิทิน", "ดูงานตามเวลาและวางแผนสัปดาห์ของคุณ")
    selected_day = st.date_input("เลือกวันที่", value=date(2026, 4, 19))
    left, right = st.columns([1.4, 0.8])
    with left:
        st.markdown(
            """
            <div class='card'>
              <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div class='card-title'>เมษายน 2026</div>
                <div class='muted'>เดือน · สัปดาห์ · วัน</div>
              </div>
              <div style='margin-top:1rem; display:grid; grid-template-columns: repeat(7, 1fr); gap:.6rem;'>
                <div class='task-row' style='min-height:84px;'><b>จ. 15</b><div class='small muted'>-</div></div>
                <div class='task-row' style='min-height:84px;'><b>อ. 16</b><div class='small muted'>ประชุมเช้า</div></div>
                <div class='task-row' style='min-height:84px;'><b>พ. 17</b><div class='small muted'>AI วางแผน</div></div>
                <div class='task-row' style='min-height:84px;'><b>พฤ. 18</b><div class='small muted'>ประชุม</div></div>
                <div class='task-row' style='min-height:84px;'><b>ศ. 19</b><div class='small muted'>รายงาน</div></div>
                <div class='task-row' style='min-height:84px;'><b>ส. 20</b><div class='small muted'>-</div></div>
                <div class='task-row' style='min-height:84px;'><b>อา. 21</b><div class='small muted'>-</div></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        todays_tasks = [t for t in tasks if t.get('due_date') == selected_day.isoformat()]
        st.markdown("<div class='card'><div class='card-title'>วันที่เลือก</div>", unsafe_allow_html=True)
        st.write(selected_day.strftime('%d %b %Y'))
        if todays_tasks:
            for t in todays_tasks:
                st.markdown(f"<div class='task-row'><b>{t.get('title')}</b><div class='small muted'>{t.get('status')}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='task-row'><div class='small muted'>ไม่มีงานในวันนี้</div></div>", unsafe_allow_html=True)
        if st.button("+ เพิ่มงานด่วน", use_container_width=True):
            st.session_state["show_add_task"] = True
            st.success("เปิดฟอร์มเพิ่มงานด่วนด้านบนแล้ว")
        st.markdown("</div>", unsafe_allow_html=True)


def render_ai_planner():
    render_header("AI วางแผน", "ใช้ AI เฉพาะเวลาที่ต้องการสรุปหรือช่วยจัดแผน")
    goal = st.selectbox("เลือกเป้าหมาย", ["สรุปงานของฉัน", "วางแผนสัปดาห์", "แตกเป้าหมายเป็นงาน", "สรุปบันทึกการประชุม"])
    c1, c2 = st.columns([1.1, 0.9])
    with c1:
        prompt = st.text_area("ข้อความตั้งต้น", placeholder="อธิบายเป้าหมาย บันทึกการประชุม หรือสิ่งที่อยากให้ช่วยวางแผน...", height=180)
        if st.button("สร้างแผน", use_container_width=True):
            st.session_state["ai_result"] = f"ผลลัพธ์ตัวอย่างสำหรับ: {goal}"
    with c2:
        result = st.session_state.get("ai_result", "ยังไม่มีผลลัพธ์ ลองกดสร้างแผนได้เลย")
        st.markdown(
            f"""
            <div class='card' style='min-height: 252px;'>
              <div class='card-title'>ผลลัพธ์จาก AI</div>
              <div class='small muted' style='margin-top:.8rem; line-height:1.6;'>{result}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.write("")
    c3, c4 = st.columns(2)
    with c3:
        if st.button("เพิ่มลงในงาน", use_container_width=True):
            st.success("เพิ่มลงในงานแล้ว")
    with c4:
        if st.button("บันทึกสรุป", use_container_width=True):
            st.success("บันทึกสรุปแล้ว")


def render_notes(db):
    render_header("บันทึก", "เก็บไอเดียและแปลงเป็นงานภายหลัง")
    st.session_state.setdefault("notes_data", [])
    with st.form("new_note_form", clear_on_submit=True):
        note_title = st.text_input("หัวข้อบันทึก")
        note_preview = st.text_area("เนื้อหาบันทึก")
        submit_note = st.form_submit_button("บันทึกโน้ต")
        if submit_note:
            if note_title.strip():
                new_note = {"title": note_title.strip(), "preview": note_preview.strip(), "created_at": date.today().isoformat()}
                if db is not None:
                    try:
                        db.insert_note(new_note)
                    except Exception as e:
                        st.error(f"บันทึกลงฐานข้อมูลไม่สำเร็จ: {e}")
                        st.stop()
                st.session_state["notes_data"].append(new_note)
                st.success("บันทึกแล้ว")
            else:
                st.error("กรุณาใส่หัวข้อบันทึก")
    notes = fetch_notes(db)
    for note in notes:
        st.markdown(
            f"""
            <div class='task-row'>
              <div style='font-weight:700;'>{note.get('title', '')}</div>
              <div class='small muted' style='margin-top:.25rem;'>{note.get('preview', '')}</div>
              <div style='margin-top:.55rem; display:flex; gap:.5rem; flex-wrap:wrap;'>
                <span class='pill'>เปิดดู</span><span class='pill'>สรุปด้วย AI</span><span class='pill'>แปลงเป็นงาน</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_settings(db):
    render_header("ตั้งค่า", "กำหนดค่าบัญชี ปฏิทิน และ AI")
    st.session_state.setdefault("settings_data", {"name": "", "email": "", "reminder": True, "ai_mode": "ปานกลาง"})
    settings = fetch_settings(db)
    if isinstance(settings, dict):
        st.session_state["settings_data"].update({
            "name": settings.get("name", st.session_state["settings_data"]["name"]),
            "email": settings.get("email", st.session_state["settings_data"]["email"]),
            "reminder": settings.get("reminder", st.session_state["settings_data"]["reminder"]),
            "ai_mode": settings.get("ai_mode", st.session_state["settings_data"]["ai_mode"]),
        })
    settings = st.session_state["settings_data"]
    with st.form("settings_form"):
        name = st.text_input("ชื่อผู้ใช้", value=settings["name"])
        email = st.text_input("อีเมล", value=settings["email"])
        reminder = st.toggle("เปิดการแจ้งเตือน", value=settings["reminder"])
        ai_mode = st.selectbox("ระดับการช่วยของ AI", ["น้อย", "ปานกลาง", "มาก"], index=["น้อย", "ปานกลาง", "มาก"].index(settings["ai_mode"]))
        save_settings = st.form_submit_button("บันทึกการตั้งค่า")
        if save_settings:
            payload = {"id": 1, "name": name, "email": email, "reminder": reminder, "ai_mode": ai_mode}
            if db is not None:
                try:
                    db.save_settings(payload)
                except Exception as e:
                    st.error(f"บันทึกลงฐานข้อมูลไม่สำเร็จ: {e}")
                    st.stop()
            st.session_state["settings_data"] = {"name": name, "email": email, "reminder": reminder, "ai_mode": ai_mode}
            st.success("บันทึกการตั้งค่าแล้ว")
    st.markdown("<div class='card'><div class='card-title'>เชื่อมปฏิทิน</div><div class='small muted' style='margin-top:.5rem;'>เชื่อม Google Calendar ในภายหลังเพื่อซิงก์งาน</div></div>", unsafe_allow_html=True)
    st.write("")
    st.markdown("<div class='card'><div class='card-title'>การแจ้งเตือน</div><div class='small muted' style='margin-top:.5rem;'>สรุปรายวัน การเตือน และแจ้งเตือนก่อนถึงกำหนด</div></div>", unsafe_allow_html=True)
    st.write("")
    st.markdown("<div class='card'><div class='card-title'>การตั้งค่า AI</div><div class='small muted' style='margin-top:.5rem;'>เลือกว่าต้องการให้ AI ช่วยวางแผนบ่อยแค่ไหน</div></div>", unsafe_allow_html=True)


def main():
    st.sidebar.markdown("<div class='sidebar-brand'>EzyCommunity</div><div class='muted small'>งาน · ปฏิทิน · AI วางแผน</div>", unsafe_allow_html=True)
    page = st.sidebar.radio("เมนู", NAV_ITEMS, index=0, label_visibility="collapsed")

    db = load_db()
    tasks = fetch_tasks(db)

    if db is None:
        st.sidebar.info("โหมดพรีวิว UI: ยังไม่ได้เชื่อม Supabase")
    else:
        st.sidebar.success("เชื่อม Supabase แล้ว")

    st.session_state["db"] = db

    if page == "แดชบอร์ด":
        render_dashboard(tasks)
    elif page == "งาน":
        render_tasks(tasks)
    elif page == "ปฏิทิน":
        render_calendar(tasks)
    elif page == "AI วางแผน":
        render_ai_planner()
    elif page == "บันทึก":
        render_notes(db)
    elif page == "ตั้งค่า":
        render_settings(db)


if __name__ == "__main__":
    main()
