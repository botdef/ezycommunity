import os

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


class DBManager:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.client = create_client(url, key)

    def insert_task(self, data):
        return self.client.table("tasks").insert(data).execute()

    def update_task(self, task_id, data):
        return self.client.table("tasks").update(data).eq("id", task_id).execute()

    def delete_task(self, task_id):
        return self.client.table("tasks").delete().eq("id", task_id).execute()

    def fetch_tasks(self):
        return self.client.table("tasks").select("*").order("due_date").execute()

    def insert_note(self, data):
        return self.client.table("notes").insert(data).execute()

    def fetch_notes(self):
        return self.client.table("notes").select("*").order("created_at", desc=True).execute()

    def save_settings(self, data):
        return self.client.table("settings").upsert(data).execute()

    def fetch_settings(self):
        return self.client.table("settings").select("*").limit(1).execute()

    def mark_as_done(self, task_id):
        return self.client.table("tasks").update({"status": "เสร็จแล้ว"}).eq("id", task_id).execute()
