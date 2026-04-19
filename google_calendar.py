"""Google Calendar — OAuth2 + อ่านกิจกรรม (readonly)"""
from __future__ import annotations

import json
import os
from datetime import date, datetime, time
from typing import Any, List, Optional
from zoneinfo import ZoneInfo

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
DEFAULT_TZ = "Asia/Bangkok"


def _redirect_uris_env() -> list[str]:
    raw = os.getenv("GOOGLE_REDIRECT_URI", "").strip()
    if not raw:
        return []
    return [u.strip() for u in raw.split(",") if u.strip()]


def calendar_oauth_configured() -> bool:
    cid = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    csec = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
    return bool(cid and csec)


def calendar_feature_enabled() -> bool:
    """เปิดส่วนเชื่อม Google Calendar — ค่าเริ่มต้นปิด (เชื่อมทีหลังได้)"""
    v = os.getenv("ENABLE_GOOGLE_CALENDAR", "false").strip().lower()
    return v in ("1", "true", "yes", "on")


def get_redirect_uri() -> Optional[str]:
    """ใช้ GOOGLE_REDIRECT_URI ตัวแรก (หรือคั่นด้วย comma ถ้ามีหลายตัว — ใช้ตัวแรกสำหรับ flow)"""
    uris = _redirect_uris_env()
    if uris:
        return uris[0]
    return os.getenv("GOOGLE_REDIRECT_URI", "").strip() or None


def _client_config() -> dict:
    cid = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    csec = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
    redirect = get_redirect_uri()
    web = {
        "client_id": cid,
        "client_secret": csec,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    if redirect:
        web["redirect_uris"] = [redirect]
    return {"web": web}


def build_flow(redirect_uri: str) -> Flow:
    return Flow.from_client_config(
        _client_config(),
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )


def get_authorization_url(redirect_uri: str) -> tuple[str, str]:
    flow = build_flow(redirect_uri)
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return authorization_url, state


def exchange_code(code: str, redirect_uri: str) -> str:
    flow = build_flow(redirect_uri)
    flow.fetch_token(code=code)
    creds = flow.credentials
    return creds.to_json()


def credentials_from_token_json(token_json: str) -> Optional[Credentials]:
    if not token_json:
        return None
    try:
        data = json.loads(token_json)
        return Credentials.from_authorized_user_info(data, SCOPES)
    except Exception:
        return None


def fetch_events_for_date(creds: Credentials, day: date, tz_name: str = DEFAULT_TZ) -> List[dict[str, Any]]:
    """คืนรายการ dict ที่มี summary, start_iso, end_iso, html_link"""
    tz = ZoneInfo(tz_name)
    start_dt = datetime.combine(day, time.min, tzinfo=tz)
    end_dt = datetime.combine(day, time.max, tzinfo=tz)
    time_min = start_dt.isoformat()
    time_max = end_dt.isoformat()

    try:
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
    except HttpError:
        return []
    items = events_result.get("items", [])
    out: List[dict[str, Any]] = []
    for ev in items:
        start = ev.get("start", {})
        end = ev.get("end", {})
        if "dateTime" in start:
            start_iso = start["dateTime"]
        else:
            start_iso = start.get("date", "")
        if "dateTime" in end:
            end_iso = end["dateTime"]
        else:
            end_iso = end.get("date", "")
        out.append(
            {
                "summary": ev.get("summary", "(ไม่มีชื่อ)"),
                "start_iso": start_iso,
                "end_iso": end_iso,
                "html_link": ev.get("htmlLink", ""),
            }
        )
    return out
