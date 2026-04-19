import csv
import html
import io
import os
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional

import streamlit as st
from dotenv import load_dotenv
from google.auth.transport.requests import Request

from database import DBManager
from google_calendar import (
    calendar_feature_enabled,
    calendar_oauth_configured,
    credentials_from_token_json,
    exchange_code,
    fetch_events_for_date,
    get_authorization_url,
    get_redirect_uri,
)

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


def build_completed_tasks_report_html(tasks: List[dict]) -> str:
    """HTML สำหรับเปิดในเบราว์เซอร์แล้วพิมพ์ (Ctrl+P) — escape ข้อมูลผู้ใช้แล้ว"""
    rows = []
    for t in sorted(tasks, key=lambda x: str(x.get("due_date") or ""), reverse=True):
        title = html.escape(str(t.get("title", "")))
        desc = html.escape(str(t.get("description", "")))
        due = html.escape(str(t.get("due_date", "-")))
        pri = html.escape(str(t.get("priority", "-")))
        tag = html.escape(str(t.get("tag", "-")))
        rows.append(
            f"<tr><td>{title}</td><td>{due}</td><td>{pri}</td><td>{tag}</td><td class='desc'>{desc}</td></tr>"
        )
    rows_html = "\n".join(rows) if rows else "<tr><td colspan='5'>ไม่มีข้อมูล</td></tr>"
    generated = date.today().isoformat()
    n = len(tasks)
    return f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>รายงานงานที่เสร็จแล้ว — EzyCommunity</title>
<style>
  body {{ font-family: "Sarabun", "Leelawadee UI", "Segoe UI", sans-serif; margin: 24px; color: #0f172a; }}
  h1 {{ font-size: 1.35rem; margin-bottom: 4px; }}
  .meta {{ color: #64748b; font-size: 0.9rem; margin-bottom: 20px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.92rem; }}
  th, td {{ border: 1px solid #e2e8f0; padding: 8px 10px; text-align: left; vertical-align: top; }}
  th {{ background: #f1f5f9; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  td.desc {{ white-space: pre-wrap; word-break: break-word; }}
  @media print {{
    body {{ margin: 12mm; }}
    @page {{ size: A4; margin: 15mm; }}
  }}
</style>
</head>
<body>
  <h1>สรุปงานที่เสร็จแล้ว</h1>
  <p class="meta">EzyCommunity · สร้างเมื่อ {generated} · จำนวน {n} รายการ</p>
  <table>
    <thead>
      <tr><th>ชื่องาน</th><th>กำหนดส่ง</th><th>ความสำคัญ</th><th>แท็ก</th><th>รายละเอียด</th></tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</body>
</html>"""


def build_completed_tasks_csv(tasks: List[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["ชื่องาน", "กำหนดส่ง", "ความสำคัญ", "แท็ก", "รายละเอียด"])
    for t in sorted(tasks, key=lambda x: str(x.get("due_date") or ""), reverse=True):
        w.writerow(
            [
                t.get("title", ""),
                t.get("due_date", ""),
                t.get("priority", ""),
                t.get("tag", ""),
                t.get("description", ""),
            ]
        )
    return buf.getvalue()


def filter_tasks_list(tasks_data: list, q: str, status_filter: str, priority_filter: str) -> list:
    out = list(tasks_data)
    q = (q or "").strip().lower()
    if q:
        out = [
            t
            for t in out
            if q in str(t.get("title", "")).lower()
            or q in str(t.get("description", "")).lower()
            or q in str(t.get("tag", "")).lower()
        ]
    if status_filter and status_filter != "ทั้งหมด":
        out = [t for t in out if str(t.get("status", "")) == status_filter]
    if priority_filter and priority_filter != "ทั้งหมด":
        out = [t for t in out if str(t.get("priority", "")) == priority_filter]
    return out


def filter_done_by_due_range(done: List[dict], start_d: Optional[date], end_d: Optional[date]) -> List[dict]:
    if not start_d and not end_d:
        return done
    out = []
    for t in done:
        raw = t.get("due_date")
        if not raw:
            continue
        try:
            td = date.fromisoformat(str(raw)[:10])
        except Exception:
            continue
        if start_d and td < start_d:
            continue
        if end_d and td > end_d:
            continue
        out.append(t)
    return out


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

    fq1, fq2, fq3 = st.columns([1.2, 0.9, 0.9])
    with fq1:
        q = st.text_input("ค้นหา", placeholder="ชื่องาน รายละเอียด แท็ก", key="task_search_q")
    with fq2:
        sf = st.selectbox("กรองสถานะ", ["ทั้งหมด"] + STATUS_FLOW, key="task_filter_status")
    with fq3:
        pf = st.selectbox(
            "กรองความสำคัญ",
            ["ทั้งหมด", "ต่ำ", "ปานกลาง", "สูง", "เร่งด่วน"],
            key="task_filter_pri",
        )
    filtered_tasks = filter_tasks_list(tasks_data, q, sf, pf)
    st.caption(f"แสดง {len(filtered_tasks)} จาก {len(tasks_data)} งาน (กรองแล้ว)")

    groups = group_tasks(filtered_tasks)
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

    st.markdown("---")
    with st.expander("ส่งออกงานที่เสร็จแล้ว (พิมพ์ / สำรอง)"):
        done_all = [t for t in tasks_data if t.get("status") == "เสร็จแล้ว"]
        use_range = st.checkbox("กรองตามกำหนดส่ง (ช่วงวันที่)", value=False)
        start_d = end_d = None
        if use_range:
            cda, cdb = st.columns(2)
            with cda:
                start_d = st.date_input("ตั้งแต่", value=date.today().replace(day=1), key="export_start")
            with cdb:
                end_d = st.date_input("ถึง", value=date.today(), key="export_end")
        done = filter_done_by_due_range(done_all, start_d, end_d) if use_range else done_all
        st.caption(
            f"งาน «เสร็จแล้ว» ที่ตรงเงื่อนไข: **{len(done)}** รายการ (ทั้งหมด {len(done_all)} รายการ)"
        )
        if not done:
            st.info("ไม่มีงานที่เสร็จแล้วตามเงื่อนไข — ปรับช่วงวันที่หรือรอมีงานที่ปิดแล้ว")
        else:
            report_html = build_completed_tasks_report_html(done)
            fname_html = f"รายงานงานเสร็จแล้ว_{date.today().isoformat()}.html"
            st.download_button(
                "ดาวน์โหลด HTML (เปิดแล้วกด Ctrl+P เพื่อพิมพ์)",
                data=report_html.encode("utf-8"),
                file_name=fname_html,
                mime="text/html; charset=utf-8",
                use_container_width=True,
            )
            csv_data = build_completed_tasks_csv(done)
            st.download_button(
                "ดาวน์โหลด CSV (เปิดใน Excel / สำรองข้อมูล)",
                data=("\ufeff" + csv_data).encode("utf-8"),
                file_name=f"งานเสร็จแล้ว_{date.today().isoformat()}.csv",
                mime="text/csv; charset=utf-8",
                use_container_width=True,
            )


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
    render_header("ปฏิทิน", "งานในระบบตามวันที่ — Google Calendar เชื่อมได้ภายหลัง (อ่านอย่างเดียว)")
    redirect_uri = get_redirect_uri()
    qp = st.query_params

    def _qp_first(key: str):
        v = qp.get(key)
        if v is None:
            return None
        if isinstance(v, (list, tuple)):
            return v[0] if v else None
        return v

    if calendar_feature_enabled():
        if _qp_first("error"):
            st.warning(f"Google แจ้ง: {_qp_first('error')} — ลองเชื่อมใหม่ได้จากปุ่มด้านล่าง")
        if (
            calendar_oauth_configured()
            and redirect_uri
            and _qp_first("code")
            and _qp_first("state")
        ):
            code = _qp_first("code")
            state = _qp_first("state")
            if state != st.session_state.get("gcal_oauth_state"):
                st.error("รหัส state ไม่ตรง — กดเชื่อม Google Calendar ใหม่อีกครั้ง")
            else:
                try:
                    token_json = exchange_code(code, redirect_uri)
                    st.session_state["google_calendar_token"] = token_json
                    for k in ("gcal_auth_url", "gcal_oauth_state"):
                        st.session_state.pop(k, None)
                    try:
                        st.query_params.clear()
                    except Exception:
                        for k2 in ("code", "state", "scope"):
                            if k2 in st.query_params:
                                del st.query_params[k2]
                    st.success("เชื่อม Google Calendar แล้ว")
                    st.rerun()
                except Exception as e:
                    st.error(f"แลกรหัส OAuth ไม่สำเร็จ: {e}")
    else:
        st.info(
            "การเชื่อม **Google Calendar** ปิดไว้เป็นค่าเริ่มต้น — เมื่อพร้อมให้ตั้ง "
            "`ENABLE_GOOGLE_CALENDAR=true` และค่า OAuth ตาม **README**"
        )

    selected_day = st.date_input("เลือกวันที่", value=date.today())

    gcal_token = st.session_state.get("google_calendar_token")
    gcal_creds = credentials_from_token_json(gcal_token) if gcal_token else None

    left, right = st.columns([1.4, 0.8])
    with left:
        st.markdown(
            "<div class='card'><div class='card-title'>Google Calendar</div>",
            unsafe_allow_html=True,
        )
        if not calendar_feature_enabled():
            st.caption("เปิดใช้เมื่อพร้อมเชื่อม — ดูวิธีใน README")
        elif not calendar_oauth_configured():
            st.info(
                "ตั้งค่า `GOOGLE_CLIENT_ID` และ `GOOGLE_CLIENT_SECRET` ใน `.env` หรือ Secrets บน Streamlit "
                "แล้วเปิด Calendar API ใน Google Cloud Console"
            )
        elif not redirect_uri:
            st.warning(
                "ตั้งค่า `GOOGLE_REDIRECT_URI` ให้ตรงกับ URL ของแอป (เช่น `http://localhost:8501/` หรือ `https://xxx.streamlit.app/`)"
            )
        else:
            conn = st.columns([1, 1])
            with conn[0]:
                if st.button("เชื่อม Google Calendar", use_container_width=True):
                    url, oauth_state = get_authorization_url(redirect_uri)
                    st.session_state["gcal_oauth_state"] = oauth_state
                    st.session_state["gcal_auth_url"] = url
            with conn[1]:
                if st.session_state.get("gcal_auth_url"):
                    st.link_button(
                        "เปิดหน้าอนุญาต Google",
                        st.session_state["gcal_auth_url"],
                        type="primary",
                        use_container_width=True,
                    )
            if st.session_state.get("google_calendar_token"):
                if st.button("ตัดการเชื่อม Google Calendar", use_container_width=True):
                    st.session_state.pop("google_calendar_token", None)
                    st.session_state.pop("gcal_auth_url", None)
                    st.session_state.pop("gcal_oauth_state", None)
                    st.rerun()

        if calendar_feature_enabled() and gcal_creds:
            if getattr(gcal_creds, "expired", False) and getattr(gcal_creds, "refresh_token", None):
                try:
                    gcal_creds.refresh(Request())
                    st.session_state["google_calendar_token"] = gcal_creds.to_json()
                except Exception:
                    st.warning("โทเคน Google หมดอายุ — กดตัดการเชื่อมแล้วล็อกอินใหม่")
            events = fetch_events_for_date(gcal_creds, selected_day)
            if events:
                for ev in events:
                    line = f"**{ev['summary']}**  \n<small>{ev['start_iso'][:16]} → {ev['end_iso'][:16]}</small>"
                    if ev.get("html_link"):
                        st.markdown(f"{line}  \n[เปิดใน Google Calendar]({ev['html_link']})", unsafe_allow_html=True)
                    else:
                        st.markdown(line, unsafe_allow_html=True)
            else:
                st.caption("ไม่มีกิจกรรมในวันนี้ (หรือดึงไม่ได้)")
        elif calendar_feature_enabled() and calendar_oauth_configured() and redirect_uri:
            st.caption("ยังไม่ได้เชื่อม — กดปุ่มด้านบนแล้วล็อกอิน Google")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class='card' style='margin-top:1rem;'>
              <div class='card-title'>สัปดาห์นี้ (ภาพรวม)</div>
              <div class='muted small' style='margin-top:.4rem;'>รายละเอียดตามวันที่เลือกด้านขวา · เชื่อม Google ได้ภายหลัง</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        todays_tasks = [t for t in tasks if t.get("due_date") == selected_day.isoformat()]
        st.markdown("<div class='card'><div class='card-title'>งานในระบบ (วันที่เลือก)</div>", unsafe_allow_html=True)
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
    render_header("AI วางแผน", "ใช้ Gemini เมื่อใส่ GEMINI_API_KEY — ไม่มีคีย์จะเป็นตัวอย่างเท่านั้น")
    goal = st.selectbox("เลือกเป้าหมาย", ["สรุปงานของฉัน", "วางแผนสัปดาห์", "แตกเป้าหมายเป็นงาน", "สรุปบันทึกการประชุม"])
    c1, c2 = st.columns([1.1, 0.9])
    with c1:
        prompt_text = st.text_area(
            "ข้อความตั้งต้น",
            placeholder="อธิบายเป้าหมาย บันทึกการประชุม หรือสิ่งที่อยากให้ช่วยวางแผน...",
            height=180,
        )
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.caption("ยังไม่มี `GEMINI_API_KEY` / `GOOGLE_API_KEY` — ใส่ใน `.env` หรือ Streamlit Secrets")
        if st.button("สร้างแผน", use_container_width=True):
            user_prompt = (prompt_text or "").strip()
            if api_key:
                try:
                    import google.generativeai as genai

                    genai.configure(api_key=api_key)
                    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
                    model = genai.GenerativeModel(model_name)
                    full = f"บทบาท: ผู้ช่วยวางแผนงานภาษาไทย\nเป้าหมาย: {goal}\n\nข้อความผู้ใช้:\n{user_prompt or '(ว่าง)'}"
                    resp = model.generate_content(full)
                    st.session_state["ai_result"] = getattr(resp, "text", None) or str(resp)
                except Exception as e:
                    st.session_state["ai_result"] = f"เรียก Gemini ไม่สำเร็จ: {e}"
            else:
                st.session_state["ai_result"] = (
                    f"[ตัวอย่าง — ใส่ API Key แล้วลองใหม่]\nเป้าหมาย: {goal}\nข้อความ: {user_prompt or '(ว่าง)'}"
                )
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
    for i, note in enumerate(notes):
        row1, row2 = st.columns([4, 1])
        with row1:
            st.markdown(
                f"""
                <div class='task-row'>
                  <div style='font-weight:700;'>{note.get('title', '')}</div>
                  <div class='small muted' style='margin-top:.25rem;'>{note.get('preview', '')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with row2:
            if st.button("ลบ", key=f"note_del_{note.get('id', i)}", use_container_width=True):
                if db is not None and note.get("id") is not None:
                    try:
                        db.delete_note(note["id"])
                    except Exception as e:
                        st.error(f"ลบไม่สำเร็จ: {e}")
                        st.stop()
                else:
                    st.session_state["notes_data"] = [
                        n
                        for n in st.session_state.get("notes_data", [])
                        if (
                            n.get("title"),
                            n.get("created_at"),
                            n.get("preview"),
                        )
                        != (
                            note.get("title"),
                            note.get("created_at"),
                            note.get("preview"),
                        )
                    ]
                st.rerun()


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
    st.markdown(
        "<div class='card'><div class='card-title'>เชื่อมปฏิทิน</div><div class='small muted' style='margin-top:.5rem;'>"
        "ตั้ง <code>ENABLE_GOOGLE_CALENDAR=true</code> และ OAuth ตาม README เมื่อพร้อมเชื่อม Google Calendar</div></div>",
        unsafe_allow_html=True,
    )
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
