const navItems = [
  { name: 'แดชบอร์ด', active: true },
  { name: 'งาน', active: false },
  { name: 'ปฏิทิน', active: false },
  { name: 'AI Planner', active: false },
  { name: 'บันทึก', active: false },
  { name: 'ตั้งค่า', active: false },
];

const stats = [
  { label: 'งานทั้งหมด', value: '24', delta: '+3', tone: 'from-sky-500 to-cyan-400' },
  { label: 'ต้องทำวันนี้', value: '5', delta: '2 ด่วน', tone: 'from-indigo-500 to-violet-400' },
  { label: 'กำลังทำ', value: '3', delta: 'กำลังเดินหน้า', tone: 'from-blue-500 to-sky-300' },
  { label: 'เสร็จแล้ว', value: '12', delta: 'อัปเดตล่าสุด', tone: 'from-emerald-500 to-teal-400' },
];

const overviewCards = [
  { title: 'โฟกัสวันนี้', value: 'Top 3', desc: 'งานสำคัญที่สุดที่ต้องทำก่อน', tone: 'from-blue-600 to-cyan-400' },
  { title: 'งานค้าง', value: '8', desc: 'งานที่ยังต้องติดตาม', tone: 'from-slate-500 to-slate-300' },
  { title: 'งานเกินกำหนด', value: '2', desc: 'ควรรีบจัดการทันที', tone: 'from-rose-500 to-pink-400' },
  { title: 'เวลาโฟกัส', value: '4 ชม.', desc: 'บล็อกเวลาให้การทำงาน', tone: 'from-emerald-500 to-teal-400' },
];

const quickActions = [
  { title: 'เพิ่มงานใหม่', desc: 'สร้าง task เร็ว ๆ', icon: '+' },
  { title: 'เปิด AI Planner', desc: 'สรุปและจัดลำดับงาน', icon: 'AI' },
  { title: 'ดูงานเกินกำหนด', desc: 'งานที่ต้องรีบแก้', icon: '!' },
  { title: 'เปิดปฏิทิน', desc: 'ดูงานตามเวลา', icon: '◷' },
];

const focusTasks = [
  { title: 'สรุปรายงานประจำสัปดาห์', status: 'เกินกำหนด', priority: 'ด่วน', due: '19 เม.ย.', tag: 'งาน' },
  { title: 'จดบันทึกประชุมทีม', status: 'กำลังทำ', priority: 'กลาง', due: '19 เม.ย.', tag: 'Admin' },
  { title: 'เตรียมแผนงานสัปดาห์หน้า', status: 'ยังไม่ได้เริ่ม', priority: 'ด่วน', due: '21 เม.ย.', tag: 'Planning' },
];

const taskColumns = [
  {
    title: 'งานเกินกำหนด',
    badge: '2',
    tone: 'border-rose-500/30 bg-rose-500/10',
    items: [
      { title: 'ส่งไฟล์สรุป', due: '18 เม.ย.', priority: 'ด่วน' },
      { title: 'ตอบ feedback ลูกค้า', due: '17 เม.ย.', priority: 'สูง' },
    ],
  },
  {
    title: 'ยังไม่ได้เริ่ม',
    badge: '4',
    tone: 'border-slate-500/30 bg-slate-500/10',
    items: [
      { title: 'วางแผนประชาสัมพันธ์', due: '22 เม.ย.', priority: 'กลาง' },
      { title: 'รีวิวเอกสารโปรเจกต์', due: '23 เม.ย.', priority: 'ต่ำ' },
    ],
  },
  {
    title: 'กำลังทำ',
    badge: '3',
    tone: 'border-sky-500/30 bg-sky-500/10',
    items: [
      { title: 'เขียนรายงานสรุป', due: '19 เม.ย.', priority: 'สูง' },
      { title: 'จดบันทึกประชุม', due: '19 เม.ย.', priority: 'กลาง' },
    ],
  },
  {
    title: 'เสร็จแล้ว',
    badge: '12',
    tone: 'border-emerald-500/30 bg-emerald-500/10',
    items: [
      { title: 'ตรวจปฏิทิน', due: '20 เม.ย.', priority: 'ต่ำ' },
      { title: 'อัปเดต task flow', due: '18 เม.ย.', priority: 'กลาง' },
    ],
  },
];

const timeline = ['09:00 ประชุมทีม', '11:00 เขียนรายงาน', '14:00 คุยลูกค้า', '16:00 ตรวจปฏิทิน'];

const calendarDays = [
  ['15', '-'],
  ['16', 'ประชุมทีม'],
  ['17', 'AI Plan'],
  ['18', 'Meeting'],
  ['19', 'Report'],
  ['20', '-'],
  ['21', '-'],
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[#0f172a] font-sans text-white">
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.22),_transparent_26%),radial-gradient(circle_at_top_right,_rgba(14,165,233,0.16),_transparent_24%),linear-gradient(180deg,_#0f172a_0%,_#111827_40%,_#0f172a_100%)]" />

      <div className="mx-auto flex min-h-screen max-w-7xl gap-6 px-4 py-4 lg:px-6">
        <aside className="hidden w-72 shrink-0 rounded-[28px] border border-white/10 bg-[#1e293b] p-5 shadow-[0_24px_60px_rgba(0,0,0,0.35)] lg:block">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-600 text-lg font-black text-white shadow-lg shadow-blue-500/20">E</div>
            <div>
              <div className="text-lg font-extrabold tracking-tight text-white">EzyCommunity</div>
              <p className="text-xs text-slate-400">Task + Calendar + AI Planner</p>
            </div>
          </div>

          <div className="mt-6 rounded-3xl border border-white/10 bg-[#0f172a] p-4">
            <div className="text-sm font-semibold text-white">วันนี้ต้องโฟกัส</div>
            <div className="mt-1 text-xs leading-5 text-slate-400">มีงานเร่งด่วน 2 งาน และงานค้าง 8 รายการ</div>
          </div>

          <nav className="mt-6 space-y-2 text-sm font-medium text-slate-300">
            {navItems.map((item) => (
              <button
                key={item.name}
                className={`flex w-full items-center rounded-xl px-4 py-3 text-left transition duration-200 ${item.active ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'hover:bg-blue-600 hover:text-white'}`}
              >
                {item.name}
              </button>
            ))}
          </nav>

          <div className="mt-6 rounded-[24px] border border-blue-500/20 bg-[#0f172a] p-5 text-white shadow-xl shadow-blue-500/10">
            <div className="text-sm font-semibold">Quick AI</div>
            <p className="mt-2 text-xs leading-5 text-slate-400">ใช้ AI เฉพาะตอนที่ต้องวางแผน สรุป หรือจัดลำดับงาน</p>
            <button className="mt-4 rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-500">
              เปิด AI Planner
            </button>
          </div>
        </aside>

        <section className="flex-1 space-y-6">
          <header className="rounded-[32px] border border-white/10 bg-[#1e293b] px-6 py-5 shadow-[0_24px_60px_rgba(0,0,0,0.28)] lg:px-8">
            <div className="flex flex-col gap-5">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm text-slate-400">สวัสดี, คุณผู้ใช้</p>
                  <h1 className="mt-1 text-3xl font-black tracking-tight lg:text-5xl">
                    Dark Blue <span className="bg-gradient-to-r from-sky-400 to-blue-400 bg-clip-text text-transparent">Dashboard</span>
                  </h1>
                  <p className="mt-2 max-w-2xl text-sm text-slate-400">จัดการงาน ปฏิทิน และ AI Planner ในโครงสร้างเว็บแอปที่ดูทันสมัย</p>
                </div>
                <div className="hidden items-center gap-3 lg:flex">
                  <button className="rounded-2xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:bg-blue-500">
                    + เพิ่มงาน
                  </button>
                  <button className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-white transition hover:bg-white/10">
                    ใช้ AI วางแผน
                  </button>
                </div>
              </div>

              <div className="grid gap-3 lg:grid-cols-[1.2fr_0.8fr]">
                <div className="rounded-[24px] border border-white/10 bg-[#0f172a] p-3">
                  <label className="mb-2 block text-xs font-medium text-slate-400">ค้นหางาน, โน้ต หรือชื่อโปรเจกต์</label>
                  <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-[#0b1224] px-4 py-3 text-white shadow-sm">
                    <span className="text-slate-500">⌕</span>
                    <span className="text-sm text-slate-400">พิมพ์เพื่อค้นหา...</span>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-3">
                  {['วันนี้', 'สัปดาห์นี้', 'เดือนนี้'].map((item, index) => (
                    <div key={item} className="rounded-[24px] border border-white/10 bg-[#0f172a] p-3 text-center shadow-sm transition hover:scale-[1.02] hover:border-blue-500/30">
                      <div className="text-xs text-slate-400">{item}</div>
                      <div className="mt-1 text-sm font-semibold text-white">{index === 0 ? '5 งาน' : index === 1 ? '18 งาน' : '24 งาน'}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </header>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {stats.map((stat) => (
              <div
                key={stat.label}
                className="rounded-[28px] border border-white/10 bg-[#1e293b] p-5 shadow-[0_16px_40px_rgba(0,0,0,0.22)] transition duration-200 hover:scale-[1.03] hover:border-blue-500/30"
              >
                <div className={`h-1.5 w-16 rounded-full bg-gradient-to-r ${stat.tone}`} />
                <p className="mt-4 text-sm text-slate-400">{stat.label}</p>
                <div className="mt-2 text-3xl font-black tracking-tight text-white">{stat.value}</div>
                <p className="mt-2 text-xs text-slate-400">{stat.delta}</p>
              </div>
            ))}
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {overviewCards.map((card) => (
              <div key={card.title} className="rounded-[28px] border border-white/10 bg-[#1e293b] p-5 shadow-[0_16px_40px_rgba(0,0,0,0.22)] transition duration-200 hover:scale-[1.03] hover:-translate-y-0.5 hover:border-blue-500/30">
                <div className={`h-1.5 w-14 rounded-full bg-gradient-to-r ${card.tone}`} />
                <div className="mt-4 text-sm text-slate-400">{card.title}</div>
                <div className="mt-2 text-3xl font-black tracking-tight text-white">{card.value}</div>
                <div className="mt-2 text-xs leading-5 text-slate-400">{card.desc}</div>
              </div>
            ))}
          </div>

          <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
            <div className="space-y-6">
              <div className="rounded-[32px] border border-blue-500/20 bg-[#1e293b] p-5 shadow-[0_16px_40px_rgba(0,0,0,0.22)]">
                <div className="flex items-center justify-between">
                  <h2 className="font-semibold text-white">Quick Actions</h2>
                  <span className="text-sm text-slate-400">ปุ่มลัด</span>
                </div>
                <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                  {quickActions.map((action) => (
                    <button
                      key={action.title}
                      className="rounded-[24px] border border-white/10 bg-[#0f172a] p-4 text-left transition hover:-translate-y-0.5 hover:bg-[#111c33] hover:shadow-lg"
                    >
                      <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-blue-600 text-sm font-black text-white shadow-lg shadow-blue-500/20">
                        {action.icon}
                      </div>
                      <div className="mt-4 font-semibold text-white">{action.title}</div>
                      <div className="mt-1 text-xs text-slate-400">{action.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="rounded-[32px] border border-blue-500/20 bg-[#1e293b] p-5 shadow-[0_16px_40px_rgba(0,0,0,0.22)]">
                <div className="flex items-center justify-between">
                  <h2 className="font-semibold text-white">งานสำคัญตอนนี้</h2>
                  <div className="flex gap-2 text-xs">
                    <span className="rounded-full bg-rose-500/15 px-3 py-1 text-rose-200">Overdue</span>
                    <span className="rounded-full bg-sky-500/15 px-3 py-1 text-sky-200">In Progress</span>
                    <span className="rounded-full bg-emerald-500/15 px-3 py-1 text-emerald-200">Done</span>
                  </div>
                </div>
                <div className="mt-4 space-y-3">
                  {focusTasks.map((task) => (
                    <article key={task.title} className="rounded-[22px] border border-white/10 bg-[#0f172a] p-4 transition hover:-translate-y-0.5 hover:border-blue-500/30 hover:shadow-lg">
                      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                        <div>
                          <div className="font-semibold text-white">{task.title}</div>
                          <div className="mt-1 text-sm text-slate-400">ครบกำหนด: {task.due}</div>
                        </div>
                        <div className="flex flex-wrap gap-2 text-xs font-medium">
                          <span className="rounded-full bg-red-500/15 px-3 py-1 text-red-200">{task.priority}</span>
                          <span className="rounded-full bg-white/8 px-3 py-1 text-slate-300">{task.tag}</span>
                          <span
                            className={`rounded-full px-3 py-1 font-semibold ${
                              task.status === 'กำลังทำ'
                                ? 'bg-sky-500/15 text-sky-200'
                                : task.status === 'รออยู่'
                                  ? 'bg-amber-500/15 text-amber-200'
                                  : task.status === 'เกินกำหนด'
                                    ? 'bg-rose-500/15 text-rose-200'
                                    : task.status === 'เสร็จแล้ว'
                                      ? 'bg-emerald-500/15 text-emerald-200'
                                      : 'bg-slate-500/15 text-slate-200'
                            }`}
                          >
                            {task.status}
                          </span>
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              </div>

              <div className="grid gap-4 lg:grid-cols-2">
                {taskColumns.map((column) => (
                  <div key={column.title} className={`rounded-[32px] border p-5 shadow-[0_16px_40px_rgba(0,0,0,0.22)] ${column.tone}`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <h2 className="font-semibold text-white">{column.title}</h2>
                        <p className="mt-1 text-xs text-slate-400">สถานะงานแบบแยกชัด</p>
                      </div>
                      <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-white">{column.badge}</span>
                    </div>
                    <div className="mt-4 space-y-3">
                      {column.items.map((item) => (
                        <div key={item.title} className="rounded-[20px] border border-white/10 bg-[#0f172a] px-4 py-3 shadow-sm transition hover:bg-[#111c33]">
                          <div className="font-medium text-white">{item.title}</div>
                          <div className="mt-1 flex items-center justify-between text-xs text-slate-400">
                            <span>ครบกำหนด {item.due}</span>
                            <span className="rounded-full bg-white/8 px-2 py-1 font-semibold text-slate-200">{item.priority}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <aside className="space-y-6">
              <div className="rounded-[32px] border border-blue-500/20 bg-[#1e293b] p-5 shadow-[0_16px_40px_rgba(0,0,0,0.22)]">
                <div className="flex items-center justify-between">
                  <h2 className="font-semibold text-white">AI Summary</h2>
                  <span className="rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-semibold text-emerald-200">พร้อมใช้งาน</span>
                </div>
                <p className="mt-4 text-sm leading-7 text-slate-400">
                  วันนี้ควรโฟกัสงานด่วน 2 งานแรก แล้วค่อยจัดการงานที่มีเดดไลน์พรุ่งนี้
                </p>
                <button className="mt-4 rounded-2xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-500">
                  เปิด AI Planner
                </button>
                <div className="mt-4 flex flex-wrap gap-2">
                  {['สรุปงานวันนี้', 'วางแผนสัปดาห์', 'แตกงานย่อย', 'สรุปโน้ตประชุม'].map((item) => (
                    <span key={item} className="rounded-full bg-white/8 px-3 py-1 text-xs font-medium text-slate-300">
                      {item}
                    </span>
                  ))}
                </div>
              </div>

              <div className="rounded-[32px] border border-blue-500/20 bg-[#1e293b] p-5 shadow-[0_16px_40px_rgba(0,0,0,0.22)]">
                <div className="flex items-center justify-between">
                  <h2 className="font-semibold text-white">ปฏิทินวันนี้</h2>
                  <span className="text-sm text-slate-400">19 เม.ย. 2026</span>
                </div>
                <div className="mt-4 space-y-3 text-sm">
                  {timeline.map((item, index) => (
                    <div key={item} className="flex items-start gap-3 rounded-[20px] bg-[#0f172a] px-4 py-3 text-slate-300 transition hover:bg-[#111c33]">
                      <div className="mt-1 h-2.5 w-2.5 rounded-full bg-gradient-to-r from-sky-400 to-indigo-500 shadow-md shadow-sky-500/30" />
                      <div>
                        <div className="font-medium text-white">{item}</div>
                        <div className="text-xs text-slate-400">บล็อกเวลา {index + 1}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </aside>
          </div>
        </section>
      </div>
    </main>
  );
}
