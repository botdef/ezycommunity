import os
from dataclasses import dataclass
from datetime import date, datetime
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


TASKS_SEED: List[Task] = [
    Task("เตรียมรายงานประจำสัปดาห์", "สรุปความคืบหน้าและความเสี่ยงที่อาจเกิดขึ้น", "2026-04-19", "สูง", "เกินกำหนด", "งาน"),
    Task("จดบันทึกการประชุมทีม", "รวบรวมมติและรายการงานที่ต้องดำเนินการ", "2026-04-19", "ปานกลาง", "กำลังทำ", "งานแอดมิน"),
    Task("ตรวจสอบการเชื่อมปฏิทิน", "เช็กว่างานถูกผูกกับปฏิทินหรือยัง", "2026-04-20", "ต่ำ", "เสร็จแล้ว", "ระบบ"),
    Task("วางแผนประชาสัมพันธ์ชุมชน", "ร่างไทม์ไลน์กิจกรรมสำหรับสัปดาห์หน้า", "2026-04-21", "เร่งด่วน", "ยังไม่ได้เริ่ม", "ชุมชน"),
    Task("เตรียมข้อเสนอโปรเจกต์", "ร่าง outline และนำเสนอให้ทีมตรวจทาน", "2026-04-22", "สูง", "ยังไม่ได้เริ่ม", "Planning"),
    Task("ประชุมทีมออนไลน์", "สรุป OKR รายไตรมาส", "2026-04-22", "ปานกลาง", "ยังไม่ได้เริ่ม", "งาน"),
    Task("รอข้อมูลจากลูกค้า", "รอไฟล์และคำตอบจากฝั่งลูกค้า", "2026-04-23", "ต่ำ", "รออยู่", "Waiting"),
]

NAV_ITEMS = ["แดชบอร์ด", "งาน", "เร่งด่วน", "นัดประชุม", "ปฏิทิน", "AI วางแผน", "บันทึก", "ตั้งค่า"]
STATUS_FLOW = ["ยังไม่ได้เริ่ม", "กำลังทำ", "รออยู่", "เกินกำหนด", "เสร็จแล้ว", "เร่งด่วน"]


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
      .kanban-col {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 22px;
        padding: 1rem;
        min-height: 220px;
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
      div[data-baseweb="select"] > div {
        border-radius: 14px;
        border-color: #dbeafe;
        background: #eff6ff;
      }
      div[data-baseweb="select"] span {
        color: #1d4ed8;
        font-weight: 600;
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


def persist_task(db: Optional[DBManager], task: dict):
    if db is None:
        return None
    return db.insert_task(task)


def update_task(db: Optional[DBManager], task_id, payload: dict):
    if db is None or task_id is None:
        return None
    return db.update_task(task_id, payload)


def delete_task(db: Optional[DBManager], task_id):
    if db is None or task_id is None:
        return None
    return db.client.table("tasks").delete().eq("id", task_id).execute()


def fetch_tasks(db: Optional[DBManager]):
    if db is None:
        return [task.__dict__ for task in TASKS_SEED]
    try:
        result = db.fetch_tasks()
        if getattr(result, "data", None):
            return result.data
    except Exception:
        pass
    return [task.__dict__ for task in TASKS_SEED]


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


def task_lookup_index(tasks, task):
    task_id = task.get("id")
    if task_id is not None:
        for i, item in enumerate(tasks):
            if item.get("id") == task_id:
                return i
    for i, item in enumerate(tasks):
        if item.get("title") == task.get("title") and item.get("due_date") == task.get("due_date"):
            return i
    return None


def task_badge(priority: str) -> str:
    colors = {"ต่ำ": "#94a3b8", "ปานกลาง": "#3b82f6", "สูง": "#f59e0b", "เร่งด่วน": "#ef4444"}
    return colors.get(priority, "#64748b")


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


def days_left_text(target_date_str: str):
    try:
        target = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        return (target - date.today()).days
    except Exception:
        return None


def due_badge_style(days_left):
    if days_left is None:
        return "background:#e2e8f0;color:#0f172a;"
    if days_left < 0:
        return "background:#fee2e2;color:#b91c1c;"
    if days_left == 0:
        return "background:#fecaca;color:#991b1b;"
    if days_left <= 3:
        return "background:#fef3c7;color:#b45309;"
    if days_left <= 7:
        return "background:#dbeafe;color:#1d4ed8;"
    return "background:#dcfce7;color:#166534;"


def days_breakdown_text(target_date_str: str):
    try:
        target = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        delta_days = (target - date.today()).days
        years = abs(delta_days) // 365
        months = (abs(delta_days) % 365) // 30
        days = abs(delta_days) % 30
        parts = []
        if years:
            parts.append(f"{years} ปี")
        if months:
            parts.append(f"{months} เดือน")
        if days or not parts:
            parts.append(f"{days} วัน")
        if delta_days < 0:
            return f"เลยกำหนด {' '.join(parts)}"
        if delta_days == 0:
            return "ครบกำหนดวันนี้"
        return f"เหลือ {' '.join(parts)}"
    except Exception:
        return "ไม่ทราบวัน"


def is_due_in_3_days(target_date_str: str) -> bool:
    try:
        target = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        return (target - date.today()).days == 3
    except Exception:
        return False


def due_badge_text(days_left):
    if days_left is None:
        return "ไม่ทราบวัน"
    if days_left < 0:
        return f"เลยกำหนด {abs(days_left)} วัน"
    if days_left == 0:
        return "ครบกำหนดวันนี้"
    if days_left == 1:
        return "เหลือ 1 วัน"
    return f"เหลือ {days_left} วัน"


def render_dashboard(tasks):
    render_header("แดชบอร์ด", "ดูภาพรวมงานวันนี้ เตือนประชุม และงานที่ต้องทำต่อ")

    today = date.today().isoformat()
    overdue_tasks = [t for t in tasks if t.get("due_date") and t.get("due_date") < today and t.get("status") != "เสร็จแล้ว"]
    today_tasks = [t for t in tasks if t.get("due_date") == today and t.get("status") != "เสร็จแล้ว"]
    upcoming_tasks = [t for t in tasks if t.get("due_date") and t.get("due_date") > today and t.get("status") != "เสร็จแล้ว"]
    urgent_tasks = [t for t in tasks if t.get("priority") == "เร่งด่วน" and t.get("status") != "เสร็จแล้ว"]
    meeting_tasks = [t for t in tasks if "ประชุม" in str(t.get("title", "")) or "meeting" in str(t.get("title", "")).lower()]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("งานทั้งหมด", len(tasks))
    c2.metric("กำลังทำ", sum(1 for t in tasks if t.get("status") == "กำลังทำ"))
    c3.metric("งานวันนี้", len(today_tasks))
    c4.metric("เกินกำหนด", len(overdue_tasks))

    st.markdown("### งานเร่งด่วน")
    if urgent_tasks:
        cols = st.columns(2)
        for i, task in enumerate(urgent_tasks[:4]):
            with cols[i % 2]:
                st.markdown(
                    f"<div class='task-row'><b>{task.get('title')}</b><span class='pill' style='background:#ef4444;color:white;margin-left:.5rem;'>เร่งด่วน</span><div class='muted' style='margin-top:.35rem;'>{days_breakdown_text(task.get('due_date', ''))}</div></div>",
                    unsafe_allow_html=True,
                )
    else:
        st.markdown("<div class='task-row'><div class='muted'>ไม่มีงานเร่งด่วน</div></div>", unsafe_allow_html=True)

    meeting_due_3_days = [t for t in meeting_tasks if is_due_in_3_days(t.get("due_date", ""))]
    st.write("")
    st.subheader("เตือนประชุม 3 วัน")
    if meeting_due_3_days:
        for task in meeting_due_3_days:
            st.markdown(
                f"<div class='task-row'><b>{task.get('title')}</b> <span class='pill' style='background:#f59e0b;color:white;'>อีก 3 วัน</span><div class='muted' style='margin-top:.35rem;'>เหลือ {days_breakdown_text(task.get('due_date', ''))}</div></div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown("<div class='task-row'><div class='muted'>ไม่มีประชุมที่เหลืออีก 3 วัน</div></div>", unsafe_allow_html=True)

    left, right = st.columns([1.15, 0.85])
    with left:
        st.markdown("<div class='card'><b>งานวันนี้</b><div class='muted' style='margin-top:.4rem;'>โฟกัสงานด่วนก่อน แล้วค่อยไล่ตามเดดไลน์ที่เหลือ</div></div>", unsafe_allow_html=True)
        st.write("")
        if today_tasks:
            for task in today_tasks:
                st.markdown(
                    f"<div class='task-row'><b>{task.get('title')}</b> <span class='pill' style='background:#fecaca;color:#991b1b;'>ครบกำหนดวันนี้</span><div class='muted' style='margin-top:.35rem;'>{task.get('due_date', '')}</div></div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("<div class='task-row'><div class='muted'>ไม่มีงานครบกำหนดวันนี้</div></div>", unsafe_allow_html=True)

        st.write("")
        st.subheader("เตือนส่งงานล่วงหน้า")
        upcoming_within_week = [t for t in upcoming_tasks if days_left_text(t.get("due_date", "")) is not None and 0 < days_left_text(t.get("due_date", "")) <= 7]
        if upcoming_within_week:
            for task in upcoming_within_week:
                dl = days_left_text(task.get("due_date", ""))
                st.markdown(
                    f"<div class='task-row'><b>{task.get('title')}</b> <span class='pill' style='{due_badge_style(dl)}'>{due_badge_text(dl)}</span><div class='muted' style='margin-top:.35rem;'>ครบกำหนด: {task.get('due_date', '')}</div></div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("<div class='task-row'><div class='muted'>ไม่มีงานที่ต้องเตือนภายใน 7 วัน</div></div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='card'><b>นัดประชุม</b></div>", unsafe_allow_html=True)
        if meeting_tasks:
            for task in meeting_tasks[:5]:
                dl = days_left_text(task.get("due_date", ""))
                st.markdown(
                    f"<div class='task-row'><b>{task.get('title')}</b> <span class='pill' style='{due_badge_style(dl)}'>{days_breakdown_text(task.get('due_date', ''))}</span><div class='muted' style='margin-top:.35rem;'>{task.get('due_date', '')}</div></div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("<div class='task-row'><div class='muted'>ยังไม่มีนัดประชุม</div></div>", unsafe_allow_html=True)

        st.write("")
        st.markdown("<div class='card'><b>งานถัดไป</b></div>", unsafe_allow_html=True)
        if upcoming_tasks:
            for task in sorted(upcoming_tasks, key=lambda x: x.get("due_date", ""))[:5]:
                dl = days_left_text(task.get("due_date", ""))
                st.markdown(
                    f"<div class='task-row'><b>{task.get('title')}</b> <span class='pill' style='{due_badge_style(dl)}'>{days_breakdown_text(task.get('due_date', ''))}</span><div class='muted' style='margin-top:.35rem;'>{task.get('due_date', '')}</div></div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("<div class='task-row'><div class='muted'>ไม่มีงานถัดไป</div></div>", unsafe_allow_html=True)


def group_tasks(tasks):
    groups = {s: [] for s in STATUS_FLOW}
    for task in tasks:
        status = task.get("status", "ยังไม่ได้เริ่ม")
        if status not in groups:
            status = "ยังไม่ได้เริ่ม"
        groups[status].append(task)
    return groups


def render_tasks(tasks):
    st.session_state.setdefault("tasks_data", tasks)
    tasks_data = st.session_state["tasks_data"]
    expand_add = st.session_state.pop("show_add_task", False)

    render_header("งาน", "Kanban board — เพิ่ม แก้ไข ลบ และเชื่อม Supabase")
    db = st.session_state.get("db")

    with st.expander("+ เพิ่มงานใหม่", expanded=expand_add):
        with st.form("add_task_form", clear_on_submit=True):
            title = st.text_input("ชื่องาน")
            description = st.text_area("รายละเอียด")
            c1, c2, c3 = st.columns(3)
            with c1:
                due_date = st.date_input("กำหนดส่ง", value=date.today())
            with c2:
                priority = st.selectbox("ความสำคัญ", ["ต่ำ", "ปานกลาง", "สูง", "เร่งด่วน"])
            with c3:
                tag = st.text_input("แท็ก", value="งาน")
            status = st.selectbox("สถานะ", STATUS_FLOW)
            if st.form_submit_button("บันทึกงาน", use_container_width=True):
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
                    try:
                        if db is not None:
                            persist_task(db, new_task)
                        tasks_data.append(new_task)
                        st.session_state["tasks_data"] = tasks_data
                        st.success("เพิ่มงานแล้ว")
                        st.rerun()
                    except Exception as e:
                        st.error(f"เพิ่มงานไม่สำเร็จ: {e}")

    groups = group_tasks(tasks_data)
    cols = st.columns(2)
    for i, status in enumerate(STATUS_FLOW):
        with cols[i % 2]:
            st.markdown(
                f"<div class='kanban-col'><div style='display:flex;justify-content:space-between;align-items:center;'><div class='kanban-title'>{status}</div><div class='kanban-count'>{len(groups[status])}</div></div></div>",
                unsafe_allow_html=True,
            )
            if not groups[status]:
                st.markdown("<div class='kanban-card'><div class='muted'>ยังไม่มีงาน</div></div>", unsafe_allow_html=True)
            for idx, task in enumerate(groups[status]):
                task_index = task_lookup_index(tasks_data, task)
                st.markdown(
                    f"""
                    <div class='kanban-card'>
                      <div style='font-weight:700; color:#0f172a;'>{task.get('title')}</div>
                      <div class='muted' style='margin-top:.25rem;'>{task.get('description', '')}</div>
                      <div style='margin-top:.55rem;'><span class='pill' style='background:{task_badge(task.get('priority', ''))}; color:white;'>{task.get('priority', '')}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                status_col, edit_col, delete_col = st.columns([1.4, 1, 1])
                with status_col:
                    new_status = st.selectbox(
                        "เปลี่ยนสถานะ",
                        STATUS_FLOW,
                        index=STATUS_FLOW.index(task.get("status", "ยังไม่ได้เริ่ม")) if task.get("status", "ยังไม่ได้เริ่ม") in STATUS_FLOW else 0,
                        key=f"status_select_{task_index}_{status}_{idx}",
                        label_visibility="collapsed",
                    )
                    if new_status != task.get("status") and task_index is not None:
                        tasks_data[task_index]["status"] = new_status
                        if db is not None and task.get("id") is not None:
                            update_task(db, task.get("id"), {"status": new_status})
                        st.session_state["tasks_data"] = tasks_data
                        st.rerun()
                with edit_col:
                    if st.button("แก้ไข", key=f"edit_{task_index}_{idx}", use_container_width=True):
                        st.session_state["editing_task"] = task
                        st.rerun()
                with delete_col:
                    if st.button("ลบ", key=f"delete_{task_index}_{idx}", use_container_width=True):
                        if db is not None and task.get("id") is not None:
                            delete_task(db, task.get("id"))
                        if task_index is not None:
                            tasks_data.pop(task_index)
                            st.session_state["tasks_data"] = tasks_data
                        st.success("ลบงานแล้ว")
                        st.rerun()

    editing_task = st.session_state.get("editing_task")
    if editing_task:
        st.markdown("---")
        st.subheader("แก้ไขงาน")
        with st.form("edit_task_form"):
            title = st.text_input("ชื่องาน", value=editing_task.get("title", ""))
            description = st.text_area("รายละเอียด", value=editing_task.get("description", ""))
            c1, c2, c3 = st.columns(3)
            with c1:
                due_date = st.date_input("กำหนดส่ง", value=date.fromisoformat(editing_task.get("due_date", date.today().isoformat())))
            with c2:
                priority = st.selectbox(
                    "ความสำคัญ",
                    ["ต่ำ", "ปานกลาง", "สูง", "เร่งด่วน"],
                    index=["ต่ำ", "ปานกลาง", "สูง", "เร่งด่วน"].index(editing_task.get("priority", "ปานกลาง")),
                )
            with c3:
                tag = st.text_input("แท็ก", value=editing_task.get("tag", "งาน"))
            status = st.selectbox(
                "สถานะ",
                STATUS_FLOW,
                index=STATUS_FLOW.index(editing_task.get("status", "ยังไม่ได้เริ่ม")) if editing_task.get("status", "ยังไม่ได้เริ่ม") in STATUS_FLOW else 0,
            )
            csave, ccancel = st.columns(2)
            save = csave.form_submit_button("บันทึกการแก้ไข", use_container_width=True)
            cancel = ccancel.form_submit_button("ยกเลิก", use_container_width=True)
            if save:
                updated = {
                    "title": title.strip(),
                    "description": description.strip(),
                    "due_date": due_date.isoformat(),
                    "priority": priority,
                    "status": status,
                    "tag": tag.strip() or "งาน",
                }
                idx = task_lookup_index(tasks_data, editing_task)
                if idx is not None:
                    task_id = tasks_data[idx].get("id")
                    tasks_data[idx].update(updated)
                    if db is not None and task_id is not None:
                        update_task(db, task_id, updated)
                    st.session_state["tasks_data"] = tasks_data
                st.session_state.pop("editing_task", None)
                st.success("บันทึกการแก้ไขแล้ว")
                st.rerun()
            if cancel:
                st.session_state.pop("editing_task", None)
                st.rerun()


def render_urgent(tasks):
    render_header("เร่งด่วน", "เฉพาะงานที่ตั้งความสำคัญเป็นเร่งด่วน และยังไม่เสร็จ")
    urgent = [t for t in tasks if t.get("priority") == "เร่งด่วน" and t.get("status") != "เสร็จแล้ว"]
    if not urgent:
        st.markdown("<div class='task-row'><div class='muted'>ไม่มีงานเร่งด่วน</div></div>", unsafe_allow_html=True)
        return
    for task in urgent:
        st.markdown(
            f"<div class='task-row'><b>{task.get('title')}</b><span class='pill' style='background:#ef4444;color:white;margin-left:.5rem;'>เร่งด่วน</span>"
            f"<div class='muted' style='margin-top:.35rem;'>{task.get('description', '')}</div>"
            f"<div class='muted' style='margin-top:.25rem;'>ครบกำหนด: {task.get('due_date', '-')} · {days_breakdown_text(task.get('due_date', ''))}</div></div>",
            unsafe_allow_html=True,
        )


def render_meetings(tasks):
    render_header("นัดประชุม", "งานที่หัวข้อมีคำว่าประชุม / meeting")
    meeting_tasks = [t for t in tasks if "ประชุม" in str(t.get("title", "")) or "meeting" in str(t.get("title", "")).lower()]
    if meeting_tasks:
        for task in meeting_tasks:
            st.markdown(
                f"<div class='task-row'><b>{task.get('title')}</b> <span class='pill' style='{due_badge_style(days_left_text(task.get('due_date', '')))}'>{days_breakdown_text(task.get('due_date', ''))}</span>"
                f"<div class='muted' style='margin-top:.35rem;'>วันนัด: {task.get('due_date', '')}</div></div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown("<div class='task-row'><div class='muted'>ยังไม่มีนัดประชุม</div></div>", unsafe_allow_html=True)


def render_calendar(tasks):
    render_header("ปฏิทิน", "ดูงานตามเวลาและวางแผนสัปดาห์ของคุณ")
    selected_day = st.date_input("เลือกวันที่", value=date.today())
    left, right = st.columns([1.4, 0.8])
    with left:
        st.markdown(
            """
            <div class='card'>
              <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div class='card-title'>ปฏิทิน (ตัวอย่าง UI)</div>
                <div class='muted'>เชื่อม Google Calendar ได้ในภายหลัง</div>
              </div>
              <div style='margin-top:1rem; display:grid; grid-template-columns: repeat(7, 1fr); gap:.6rem;'>
                <div class='task-row' style='min-height:84px;'><b>จ</b><div class='small muted'>-</div></div>
                <div class='task-row' style='min-height:84px;'><b>อ</b><div class='small muted'>-</div></div>
                <div class='task-row' style='min-height:84px;'><b>พ</b><div class='small muted'>-</div></div>
                <div class='task-row' style='min-height:84px;'><b>พฤ</b><div class='small muted'>-</div></div>
                <div class='task-row' style='min-height:84px;'><b>ศ</b><div class='small muted'>-</div></div>
                <div class='task-row' style='min-height:84px;'><b>ส</b><div class='small muted'>-</div></div>
                <div class='task-row' style='min-height:84px;'><b>อา</b><div class='small muted'>-</div></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        todays_tasks = [t for t in tasks if t.get("due_date") == selected_day.isoformat()]
        st.markdown("<div class='card'><div class='card-title'>วันที่เลือก</div>", unsafe_allow_html=True)
        st.write(selected_day.strftime("%d %b %Y"))
        if todays_tasks:
            for t in todays_tasks:
                st.markdown(f"<div class='task-row'><b>{t.get('title')}</b><div class='small muted'>{t.get('status')}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='task-row'><div class='small muted'>ไม่มีงานในวันนี้</div></div>", unsafe_allow_html=True)
        if st.button("+ เพิ่มงานด่วน", use_container_width=True):
            st.session_state["show_add_task"] = True
            st.success("ไปที่เมนู **งาน** — ฟอร์มเพิ่มงานจะเปิดให้")
        st.markdown("</div>", unsafe_allow_html=True)


def render_ai_planner():
    render_header("AI วางแผน", "ใช้ AI เฉพาะเวลาที่ต้องการสรุปหรือช่วยจัดแผน")
    goal = st.selectbox("เลือกเป้าหมาย", ["สรุปงานของฉัน", "วางแผนสัปดาห์", "แตกเป้าหมายเป็นงาน", "สรุปบันทึกการประชุม"])
    c1, c2 = st.columns([1.1, 0.9])
    with c1:
        st.text_area("ข้อความตั้งต้น", placeholder="อธิบายเป้าหมาย บันทึกการประชุม หรือสิ่งที่อยากให้ช่วยวางแผน...", height=180)
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
        ai_mode = st.selectbox(
            "ระดับการช่วยของ AI",
            ["น้อย", "ปานกลาง", "มาก"],
            index=["น้อย", "ปานกลาง", "มาก"].index(settings["ai_mode"]),
        )
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
    st.sidebar.markdown("<div class='sidebar-brand'>EzyCommunity</div><div class='muted small'>งาน · นัดประชุม · ปฏิทิน · AI</div>", unsafe_allow_html=True)
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
    elif page == "เร่งด่วน":
        render_urgent(tasks)
    elif page == "นัดประชุม":
        render_meetings(tasks)
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
