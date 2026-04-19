-- EzyCommunity — รันใน Supabase: SQL Editor → New query → Run
-- ตารางและคอลัมน์ให้ตรงกับ app.py / database.py

-- งาน (Kanban, แดชบอร์ด, ส่งออก)
create table if not exists public.tasks (
  id bigint generated always as identity primary key,
  title text not null default '',
  description text not null default '',
  due_date date not null default (current_date),
  priority text not null default 'ปานกลาง',
  status text not null default 'ยังไม่ได้เริ่ม',
  tag text not null default 'งาน'
);

-- บันทึก (โน้ต)
create table if not exists public.notes (
  id bigint generated always as identity primary key,
  title text not null default '',
  preview text not null default '',
  created_at date not null default (current_date)
);

-- การตั้งค่า (แถวเดียว id = 1)
create table if not exists public.settings (
  id int primary key default 1,
  name text not null default '',
  email text not null default '',
  reminder boolean not null default true,
  ai_mode text not null default 'ปานกลาง',
  constraint settings_single_row check (id = 1)
);

insert into public.settings (id, name, email, reminder, ai_mode)
values (1, '', '', true, 'ปานกลาง')
on conflict (id) do nothing;

-- RLS: ให้ client ที่ใช้ anon key ทำงานได้ (ปรับ policy ให้เข้มงวดเมื่อขึ้น production)
alter table public.tasks enable row level security;
alter table public.notes enable row level security;
alter table public.settings enable row level security;

drop policy if exists "ezy_tasks_all" on public.tasks;
create policy "ezy_tasks_all" on public.tasks for all to anon, authenticated using (true) with check (true);

drop policy if exists "ezy_notes_all" on public.notes for all to anon, authenticated using (true) with check (true);

drop policy if exists "ezy_settings_all" on public.settings for all to anon, authenticated using (true) with check (true);
