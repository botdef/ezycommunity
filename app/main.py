"""ชี้ไปที่แอปหลัก — ใช้: streamlit run app.py จาก root ของ repo (แนะนำ)"""
from pathlib import Path

import runpy

_ROOT = Path(__file__).resolve().parent.parent
runpy.run_path(str(_ROOT / "app.py"), run_name="__main__")
