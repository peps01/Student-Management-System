// ===== MOCK DATA =====

const userProfile = {
  name: 'Admin User',
  email: 'admin@school.edu',
  bio: 'System administrator at Springdale School. Managing student records and academic operations.',
  role: 'Administrator',
  joinDate: '2023-08-15',
  password: 'admin123'
};

let students = [
  { id: 1, name: 'Alice Johnson', email: 'alice@school.edu', course: 'Computer Science', year: 3 },
  { id: 2, name: 'Bob Smith', email: 'bob@school.edu', course: 'Mathematics', year: 2 },
  { id: 3, name: 'Carol Williams', email: 'carol@school.edu', course: 'Physics', year: 4 },
  { id: 4, name: 'David Brown', email: 'david@school.edu', course: 'Computer Science', year: 1 },
  { id: 5, name: 'Eva Martinez', email: 'eva@school.edu', course: 'Engineering', year: 3 },
  { id: 6, name: 'Frank Garcia', email: 'frank@school.edu', course: 'Mathematics', year: 2 },
  { id: 7, name: 'Grace Lee', email: 'grace@school.edu', course: 'Biology', year: 3 },
  { id: 8, name: 'Henry Wilson', email: 'henry@school.edu', course: 'Computer Science', year: 4 }
];

let nextStudentId = 9;

const subjects = ['Math', 'English', 'Science', 'History', 'PE'];

const gradesData = [
  { id: 1, name: 'Alice Johnson', grades: { Math: 95, English: 88, Science: 92, History: 85, PE: 90 } },
  { id: 2, name: 'Bob Smith', grades: { Math: 72, English: 80, Science: 68, History: 75, PE: 88 } },
  { id: 3, name: 'Carol Williams', grades: { Math: 88, English: 92, Science: 85, History: 90, PE: 78 } },
  { id: 4, name: 'David Brown', grades: { Math: 65, English: 70, Science: 72, History: 68, PE: 95 } },
  { id: 5, name: 'Eva Martinez', grades: { Math: 91, English: 85, Science: 89, History: 82, PE: 76 } },
  { id: 6, name: 'Frank Garcia', grades: { Math: 78, English: 74, Science: 80, History: 71, PE: 84 } },
  { id: 7, name: 'Grace Lee', grades: { Math: 93, English: 96, Science: 91, History: 94, PE: 88 } },
  { id: 8, name: 'Henry Wilson', grades: { Math: 58, English: 62, Science: 55, History: 60, PE: 70 } }
];

const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];

const attendanceData = students.map(s => ({
  id: s.id,
  name: s.name,
  records: days.map(d => Math.random() > 0.2 ? 'Present' : 'Absent')
}));

let announcements = [
  {
    id: 1,
    title: 'Welcome to Springdale School',
    body: 'We are excited to welcome all students and faculty to the new academic year. Please check your schedules and reach out to your advisors for any concerns.',
    author: 'Admin User',
    date: '2026-05-20 09:00'
  },
  {
    id: 2,
    title: 'Midterm Exam Schedule',
    body: 'Midterm examinations will begin on June 10. Please review the exam schedule posted on the bulletin board and prepare accordingly.',
    author: 'Admin User',
    date: '2026-05-22 14:30'
  },
  {
    id: 3,
    title: 'Science Fair Announcement',
    body: 'The annual Science Fair will be held on June 25. All students are encouraged to participate. Registration forms are available at the science department office.',
    author: 'Admin User',
    date: '2026-05-25 10:15'
  }
];

let nextAnncId = 4;

// ===== UTILITY FUNCTIONS =====

function getPageName() {
  const path = window.location.pathname;
  const name = path.split('/').pop().split('.')[0];
  return name || 'dashboard';
}

function getGradeClass(score) {
  if (score >= 90) return 'grade-a';
  if (score >= 75) return 'grade-b';
  if (score >= 60) return 'grade-c';
  return 'grade-d';
}

function average(arr) {
  return arr.reduce((a, b) => a + b, 0) / arr.length;
}

const avatarColors = ['#3b82f6', '#8b5cf6', '#06b6d4', '#22c55e', '#f59e0b', '#ef4444', '#ec4899', '#14b8a6'];

function getAvatarColor(name) {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return avatarColors[Math.abs(hash) % avatarColors.length];
}

function animateCounter(el, target, duration) {
  duration = duration || 800;
  const startTime = performance.now();
  function tick(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(eased * target);
    el.textContent = progress < 1 ? current : target;
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

// ===== SORT + PAGINATE UTILITIES =====

let sortState = { field: null, asc: true };

function setSort(field, renderFnName) {
  if (sortState.field === field) {
    sortState.asc = !sortState.asc;
  } else {
    sortState.field = field;
    sortState.asc = true;
  }
  if (typeof window[renderFnName] === 'function') window[renderFnName]();
}

function sortData(data) {
  if (!sortState.field) return data;
  const f = sortState.field;
  const sign = sortState.asc ? 1 : -1;
  return [...data].sort((a, b) => {
    let va = a[f], vb = b[f];
    if (f === 'year' || f === 'id') return sign * (va - vb);
    if (f === 'average') return sign * (va - vb);
    if (f === 'attPct') return sign * (va - vb);
    va = String(va).toLowerCase();
    vb = String(vb).toLowerCase();
    if (va < vb) return -sign;
    if (va > vb) return sign;
    return 0;
  });
}

function sortArrow(field) {
  if (sortState.field !== field) return '<span class="sort-arrow">↕</span>';
  return `<span class="sort-arrow">${sortState.asc ? '▲' : '▼'}</span>`;
}

function sortableHeader(label, field) {
  const active = sortState.field === field ? ' active' : '';
  return `<th class="sortable${active}" onclick="setSort('${field}', window.currentRenderFn)">${label} ${sortArrow(field)}</th>`;
}

// ===== PAGINATION =====
let currentPage = 1;
const perPage = 8;

function paginateData(data) {
  const totalPages = Math.ceil(data.length / perPage) || 1;
  if (currentPage > totalPages) currentPage = totalPages;
  const start = (currentPage - 1) * perPage;
  return data.slice(start, start + perPage);
}

function renderPagination(totalItems, renderFn) {
  const container = document.getElementById('paginationControls');
  if (!container) return;
  const totalPages = Math.ceil(totalItems / perPage) || 1;
  if (totalPages <= 1) { container.innerHTML = ''; return; }
  let html = `<button class="page-btn" onclick="goToPage(${currentPage - 1}, '${renderFn}')" ${currentPage <= 1 ? 'disabled' : ''}>&laquo; Prev</button>`;
  for (let i = 1; i <= totalPages; i++) {
    html += `<button class="page-btn${i === currentPage ? ' active' : ''}" onclick="goToPage(${i}, '${renderFn}')">${i}</button>`;
  }
  html += `<button class="page-btn" onclick="goToPage(${currentPage + 1}, '${renderFn}')" ${currentPage >= totalPages ? 'disabled' : ''}>Next &raquo;</button>`;
  html += `<span class="page-info">${totalItems} total</span>`;
  container.innerHTML = html;
}

function goToPage(page, renderFnName) {
  currentPage = page;
  if (renderFnName === 'renderStudents') renderStudents(document.getElementById('studentSearch').value);
  else if (renderFnName === 'renderGrades') renderGrades();
  else if (renderFnName === 'renderAttendance') renderAttendance();
}

// ===== TOAST SYSTEM =====

function showToast(message, type) {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${message}</span>`;
  toast.addEventListener('click', () => toast.remove());
  container.appendChild(toast);
  setTimeout(() => { if (toast.parentNode) toast.remove(); }, 3500);
}

// ===== MODAL SYSTEM =====

function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('show');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('show');
}

// Close modal on overlay click
document.addEventListener('click', function (e) {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('show');
  }
});

// ===== DARK MODE =====

function toggleDarkMode() {
  document.documentElement.classList.toggle('dark-mode');
  const isDark = document.documentElement.classList.contains('dark-mode');
  localStorage.setItem('darkMode', isDark);
  const btn = document.querySelector('.dark-mode-toggle');
  if (btn) btn.textContent = isDark ? '☀️' : '🌙';
}

function initDarkMode() {
  const btn = document.querySelector('.dark-mode-toggle');
  const isDark = document.documentElement.classList.contains('dark-mode');
  if (btn) btn.textContent = isDark ? '☀️' : '🌙';
  if (btn) btn.addEventListener('click', toggleDarkMode);
}

// ===== NOTIFICATION BELL =====

function renderBellDropdown() {
  const bell = document.querySelector('.notification-bell');
  if (!bell) return;
  const dropdown = bell.querySelector('.bell-dropdown');
  const badge = bell.querySelector('.bell-badge');
  const recent = announcements.slice(-4).reverse();
  if (badge) badge.textContent = announcements.length;
  if (!dropdown) return;
  dropdown.innerHTML = `<div class="bell-header">Recent Announcements</div>`;
  if (!recent.length) {
    dropdown.innerHTML += `<div class="bell-empty">No announcements yet</div>`;
  } else {
    recent.forEach(a => {
      dropdown.innerHTML += `
        <div class="bell-item">
          <div class="bell-item-title">${a.title}</div>
          <div class="bell-item-meta">${a.date}</div>
        </div>
      `;
    });
  }
}

function initNotificationBell() {
  const bell = document.querySelector('.notification-bell');
  if (!bell) return;
  const dropdown = bell.querySelector('.bell-dropdown');

  renderBellDropdown();

  bell.addEventListener('click', function (e) {
    renderBellDropdown();
    e.stopPropagation();
    dropdown.classList.toggle('show');
  });

  document.addEventListener('click', function () {
    dropdown.classList.remove('show');
  });
}

// ===== SIDEBAR =====

function initSidebar() {
  document.querySelectorAll('.hamburger').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelector('.sidebar').classList.toggle('open');
    });
  });
  // Highlight active nav link
  const page = getPageName();
  document.querySelectorAll('.sidebar-nav a').forEach(a => {
    const href = a.getAttribute('href');
    if (href && href.includes(page)) {
      a.classList.add('active');
    }
  });
}

// ===== AVATARS =====

function initAvatars() {
  document.querySelectorAll('.user-avatar').forEach(el => {
    const name = el.getAttribute('data-name') || userProfile.name;
    el.textContent = name.charAt(0).toUpperCase();
    el.style.background = getAvatarColor(name);
  });
}

// ===== STUDENTS PAGE =====

window.currentRenderFn = 'renderStudents';

function renderStudents(filter) {
  window.currentRenderFn = 'renderStudents';
  const table = document.getElementById('studentsTable');
  if (!table) return;
  let list = students;
  if (filter) {
    const q = filter.toLowerCase();
    list = students.filter(s =>
      s.name.toLowerCase().includes(q) ||
      s.email.toLowerCase().includes(q) ||
      s.course.toLowerCase().includes(q)
    );
  }
  const sorted = sortData(list);
  const pageData = paginateData(sorted);
  renderPagination(sorted.length, 'renderStudents');

  let html = `<thead><tr>
    ${sortableHeader('ID', 'id')}
    ${sortableHeader('Name', 'name')}
    ${sortableHeader('Email', 'email')}
    ${sortableHeader('Course', 'course')}
    ${sortableHeader('Year', 'year')}
    <th>Actions</th>
  </tr></thead><tbody>`;

  if (!pageData.length) {
    html += `<tr><td colspan="6"><div class="empty-state"><div class="empty-icon">📭</div><p>No students found</p></div></td></tr>`;
  } else {
    pageData.forEach(s => {
      html += `<tr>
        <td>${s.id}</td>
        <td><strong>${s.name}</strong></td>
        <td>${s.email}</td>
        <td>${s.course}</td>
        <td>Year ${s.year}</td>
        <td>
          <button class="btn btn-sm btn-primary" onclick="editStudent(${s.id})">Edit</button>
          <button class="btn btn-sm btn-danger" onclick="deleteStudent(${s.id})">Delete</button>
        </td>
      </tr>`;
    });
  }
  html += `</tbody>`;
  table.innerHTML = html;
}

function initStudents() {
  const searchInput = document.getElementById('studentSearch');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      currentPage = 1;
      renderStudents(this.value);
    });
  }
  renderStudents('');

  // Add form
  const form = document.getElementById('addStudentForm');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const data = new FormData(this);
      const year = parseInt(data.get('year'));
      if (year < 1 || year > 5) {
        showToast('Year must be between 1 and 5', 'error');
        return;
      }
      students.push({
        id: nextStudentId++,
        name: data.get('name'),
        email: data.get('email'),
        course: data.get('course'),
        year: year
      });
      // Also add to attendance/grades
      attendanceData.push({
        id: students[students.length - 1].id,
        name: students[students.length - 1].name,
        records: days.map(() => Math.random() > 0.2 ? 'Present' : 'Absent')
      });
      gradesData.push({
        id: students[students.length - 1].id,
        name: students[students.length - 1].name,
        grades: { Math: 0, English: 0, Science: 0, History: 0, PE: 0 }
      });
      closeModal('addStudentModal');
      this.reset();
      renderStudents(document.getElementById('studentSearch').value);
      showToast('Student added successfully', 'success');
    });
  }

  // Edit form
  const editForm = document.getElementById('editStudentForm');
  if (editForm) {
    editForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const data = new FormData(this);
      const id = parseInt(data.get('id'));
      const year = parseInt(data.get('year'));
      if (year < 1 || year > 5) {
        showToast('Year must be between 1 and 5', 'error');
        return;
      }
      const student = students.find(s => s.id === id);
      if (student) {
        student.name = data.get('name');
        student.email = data.get('email');
        student.course = data.get('course');
        student.year = year;
        // Sync names in grades/attendance
        const g = gradesData.find(g => g.id === id);
        if (g) g.name = student.name;
        const a = attendanceData.find(a => a.id === id);
        if (a) a.name = student.name;
      }
      closeModal('editStudentModal');
      renderStudents(document.getElementById('studentSearch').value);
      showToast('Student updated successfully', 'success');
    });
  }
}

function editStudent(id) {
  const student = students.find(s => s.id === id);
  if (!student) return;
  document.getElementById('editId').value = student.id;
  document.getElementById('editName').value = student.name;
  document.getElementById('editEmail').value = student.email;
  document.getElementById('editCourse').value = student.course;
  document.getElementById('editYear').value = student.year;
  openModal('editStudentModal');
}

function deleteStudent(id) {
  if (!confirm('Are you sure you want to delete this student?')) return;
  students = students.filter(s => s.id !== id);
  // Remove from grades/attendance too
  const gi = gradesData.findIndex(g => g.id === id);
  if (gi !== -1) gradesData.splice(gi, 1);
  const ai = attendanceData.findIndex(a => a.id === id);
  if (ai !== -1) attendanceData.splice(ai, 1);
  renderStudents(document.getElementById('studentSearch').value);
  showToast('Student deleted successfully', 'success');
}

// ===== GRADES PAGE =====

window.currentRenderFn = 'renderGrades';

function renderGrades() {
  window.currentRenderFn = 'renderGrades';
  const container = document.getElementById('gradesContainer');
  if (!container) return;

  const enriched = gradesData.map(g => {
    const vals = subjects.map(s => g.grades[s] || 0);
    return { ...g, average: average(vals) };
  });
  const sorted = sortData(enriched);

  let html = `
    <div class="table-container">
      <table id="gradesTable">
        <thead>
          <tr>
            ${sortableHeader('Student', 'name')}
            ${subjects.map(s => `<th>${s}</th>`).join('')}
            ${sortableHeader('Average', 'average')}
          </tr>
        </thead>
        <tbody>
  `;
  sorted.forEach(g => {
    const vals = subjects.map(s => g.grades[s] || 0);
    html += `<tr>
      <td><strong>${g.name}</strong></td>
      ${vals.map(v => `<td class="${getGradeClass(v)}">${v}</td>`).join('')}
      <td><strong class="${getGradeClass(g.average)}">${g.average.toFixed(1)}</strong></td>
    </tr>`;
  });
  html += `</tbody></table></div>`;

  // Summary cards
  const allGrades = gradesData.flatMap(g => subjects.map(s => g.grades[s] || 0));
  const overallAvg = average(allGrades);
  const highest = Math.max(...allGrades);
  const lowest = Math.min(...allGrades);

  html += `
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-top: 24px;">
      <div class="card" style="padding: 18px;">
        <p style="color: var(--text-muted); font-size: 0.8rem; margin-bottom: 4px;">Overall Average</p>
        <h3 class="${getGradeClass(overallAvg)}">${overallAvg.toFixed(1)}%</h3>
      </div>
      <div class="card" style="padding: 18px;">
        <p style="color: var(--text-muted); font-size: 0.8rem; margin-bottom: 4px;">Highest Grade</p>
        <h3 style="color: #16a34a;">${highest}%</h3>
      </div>
      <div class="card" style="padding: 18px;">
        <p style="color: var(--text-muted); font-size: 0.8rem; margin-bottom: 4px;">Lowest Grade</p>
        <h3 style="color: #dc2626;">${lowest}%</h3>
      </div>
      <div class="card" style="padding: 18px;">
        <p style="color: var(--text-muted); font-size: 0.8rem; margin-bottom: 4px;">Students</p>
        <h3>${gradesData.length}</h3>
      </div>
    </div>
  `;
  container.innerHTML = html;
}

// ===== ATTENDANCE PAGE =====

window.currentRenderFn = 'renderAttendance';

function renderAttendance() {
  window.currentRenderFn = 'renderAttendance';
  const container = document.getElementById('attendanceContainer');
  if (!container) return;

  const enriched = attendanceData.map(a => {
    const presentCount = a.records.filter(r => r === 'Present').length;
    return { ...a, attPct: (presentCount / days.length) * 100 };
  });
  const sorted = sortData(enriched);

  let html = `
    <div class="table-container">
      <table>
        <thead>
          <tr>
            ${sortableHeader('Student', 'name')}
            ${days.map(d => `<th>${d}</th>`).join('')}
            ${sortableHeader('Attendance %', 'attPct')}
          </tr>
        </thead>
        <tbody>
  `;
  sorted.forEach(a => {
    const presentCount = a.records.filter(r => r === 'Present').length;
    const pct = (presentCount / days.length) * 100;
    html += `<tr>
      <td><strong>${a.name}</strong></td>
      ${a.records.map((r, i) => `
        <td>
          <button class="att-toggle ${r.toLowerCase()}" onclick="toggleAttendance(${a.id}, ${i})">${r}</button>
        </td>
      `).join('')}
      <td>
        <span class="badge ${pct >= 80 ? 'badge-success' : pct >= 60 ? 'badge-warning' : 'badge-danger'}">
          ${pct.toFixed(0)}%
        </span>
      </td>
    </tr>`;
  });
  html += `</tbody></table></div>`;
  container.innerHTML = html;
}

function toggleAttendance(studentId, dayIndex) {
  const a = attendanceData.find(a => a.id === studentId);
  if (!a) return;
  a.records[dayIndex] = a.records[dayIndex] === 'Present' ? 'Absent' : 'Present';
  renderAttendance();
}

// ===== ANNOUNCEMENTS PAGE =====

function renderAnnouncements() {
  const container = document.getElementById('announcementsList');
  if (!container) return;
  if (!announcements.length) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">📢</div><p>No announcements yet</p></div>`;
    return;
  }
  container.innerHTML = announcements.map(a => `
    <div class="card announcement-card">
      <div class="annc-header">
        <span class="annc-title">${a.title}</span>
        <span class="annc-meta">${a.date}</span>
      </div>
      <div class="annc-body">${a.body}</div>
      <div class="annc-author">
        <span class="author-avatar">${a.author.charAt(0)}</span>
        Posted by ${a.author}
      </div>
    </div>
  `).reverse().join('');
}

function initAnnouncements() {
  const form = document.getElementById('announcementForm');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const data = new FormData(this);
      const title = data.get('title').trim();
      const body = data.get('body').trim();
      if (!title || !body) return;
      const now = new Date();
      const dateStr = now.toISOString().slice(0, 16).replace('T', ' ');
      announcements.push({
        id: nextAnncId++,
        title,
        body,
        author: 'Admin User',
        date: dateStr
      });
      closeModal('addAnnouncementModal');
      this.reset();
      renderAnnouncements();
      showToast('Announcement posted successfully', 'success');
    });
  }
  renderAnnouncements();
}

// ===== DASHBOARD CHARTS =====

function renderCourseChart() {
  const counts = {};
  students.forEach(s => { counts[s.course] = (counts[s.course] || 0) + 1; });
  const maxCount = Math.max(...Object.values(counts), 1);
  const colors = ['blue', 'green', 'purple', 'orange', 'yellow'];
  let i = 0;
  return Object.entries(counts).map(([course, count]) => {
    const pct = (count / maxCount) * 100;
    const color = colors[i++ % colors.length];
    return `
      <div class="bar-row">
        <span class="bar-label">${course}</span>
        <div class="bar-track"><div class="bar-fill ${color}" style="width:${pct}%"></div></div>
        <span class="bar-value">${count}</span>
      </div>
    `;
  }).join('');
}

function renderGradeDistChart() {
  const dist = { A: 0, B: 0, C: 0, D: 0 };
  subjects.forEach(subj => {
    gradesData.forEach(g => {
      const v = g.grades[subj] || 0;
      if (v >= 90) dist.A++;
      else if (v >= 75) dist.B++;
      else if (v >= 60) dist.C++;
      else dist.D++;
    });
  });
  const maxVal = Math.max(...Object.values(dist), 1);
  const items = [
    { label: 'A (90-100)', count: dist.A, color: 'green' },
    { label: 'B (75-89)', count: dist.B, color: 'blue' },
    { label: 'C (60-74)', count: dist.C, color: 'yellow' },
    { label: 'D (<60)', count: dist.D, color: 'red' }
  ];
  return items.map(({ label, count, color }) => `
    <div class="bar-row">
      <span class="bar-label">${label}</span>
      <div class="bar-track"><div class="bar-fill ${color}" style="width:${(count/maxVal)*100}%"></div></div>
      <span class="bar-value">${count}</span>
    </div>
  `).join('');
}

function renderAttChart() {
  const dayTotals = days.map((d, i) => {
    const p = attendanceData.filter(a => a.records[i] === 'Present').length;
    return { day: d, pct: attendanceData.length ? Math.round((p / attendanceData.length) * 100) : 0 };
  });
  return dayTotals.map(({ day, pct }) => `
    <div class="vert-bar-wrapper">
      <div class="vert-bar" style="height:${pct}%; background:${pct >= 80 ? 'var(--success)' : pct >= 60 ? 'var(--warning)' : 'var(--danger)'};"></div>
      <span class="vert-bar-label">${day}</span>
    </div>
  `).join('');
}

// ===== DASHBOARD PAGE =====

function renderDashboard() {
  const container = document.getElementById('dashboardContent');
  if (!container) return;
  const totalStudents = students.length;
  const totalSubjects = subjects.length;
  const allAttRecords = attendanceData.flatMap(a => a.records);
  const attPct = allAttRecords.length
    ? ((allAttRecords.filter(r => r === 'Present').length / allAttRecords.length) * 100).toFixed(0)
    : 0;
  const recentAnnc = announcements.slice(-3).reverse();

  container.innerHTML = `
    <div class="stat-cards">
      <div class="card stat-card">
        <div class="stat-icon blue">👥</div>
        <div class="stat-info">
          <h3 id="statStudents">0</h3>
          <p>Total Students</p>
        </div>
      </div>
      <div class="card stat-card">
        <div class="stat-icon green">📚</div>
        <div class="stat-info">
          <h3 id="statSubjects">0</h3>
          <p>Subjects</p>
        </div>
      </div>
      <div class="card stat-card">
        <div class="stat-icon yellow">📋</div>
        <div class="stat-info">
          <h3 id="statAtt">0%</h3>
          <p>Attendance Rate</p>
        </div>
      </div>
      <div class="card stat-card">
        <div class="stat-icon purple">📢</div>
        <div class="stat-info">
          <h3 id="statAnnc">0</h3>
          <p>Announcements</p>
        </div>
      </div>
    </div>

    <div class="charts-row">
      <div class="card chart-card">
        <h4>Students by Course</h4>
        <div class="bar-chart">${renderCourseChart()}</div>
      </div>
      <div class="card chart-card">
        <h4>Grade Distribution</h4>
        <div class="bar-chart">${renderGradeDistChart()}</div>
      </div>
      <div class="card chart-card">
        <h4>Weekly Attendance</h4>
        <div class="vert-bar-chart">${renderAttChart()}</div>
      </div>
      <div class="card chart-card">
        <h4>Subject Overview</h4>
        <div style="display:flex;flex-direction:column;gap:12px;justify-content:center;height:calc(100% - 34px);">
          <div><span style="color:var(--text-muted);font-size:0.85rem;">Subjects offered:</span> <strong style="font-size:1.2rem;">${totalSubjects}</strong></div>
          <div><span style="color:var(--text-muted);font-size:0.85rem;">Avg grade:</span> <strong class="${getGradeClass(average(gradesData.flatMap(g=>subjects.map(s=>g.grades[s]||0))))}" style="font-size:1.2rem;">${average(gradesData.flatMap(g=>subjects.map(s=>g.grades[s]||0))).toFixed(1)}%</strong></div>
          <div><span style="color:var(--text-muted);font-size:0.85rem;">Students enrolled:</span> <strong style="font-size:1.2rem;">${totalStudents}</strong></div>
        </div>
      </div>
    </div>

    <div class="card" style="padding: 22px;">
      <h3 style="font-size: 1.05rem; margin-bottom: 16px;">Recent Announcements</h3>
      ${recentAnnc.length ? recentAnnc.map(a => `
        <div style="padding: 12px 0; border-bottom: 1px solid var(--border);">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <strong>${a.title}</strong>
            <span style="font-size: 0.8rem; color: var(--text-muted);">${a.date}</span>
          </div>
          <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 4px;">${a.body.slice(0, 100)}${a.body.length > 100 ? '...' : ''}</p>
        </div>
      `).join('') : `<p style="color: var(--text-muted);">No announcements yet.</p>`}
    </div>
  `;

  animateCounter(document.getElementById('statStudents'), totalStudents);
  animateCounter(document.getElementById('statSubjects'), totalSubjects);
  animateCounter(document.getElementById('statAnnc'), announcements.length);

  const attEl = document.getElementById('statAtt');
  const attTarget = parseInt(attPct);
  const startTime = performance.now();
  (function tickAtt(now) {
    const p = Math.min((now - startTime) / 800, 1);
    const eased = 1 - Math.pow(1 - p, 3);
    attEl.textContent = Math.round(eased * attTarget) + '%';
    if (p < 1) requestAnimationFrame(tickAtt);
  })(performance.now());
}

// ===== PROFILE PAGE =====

function initProfile() {
  const editForm = document.getElementById('editProfileForm');
  if (editForm) {
    document.getElementById('pName').value = userProfile.name;
    document.getElementById('pEmail').value = userProfile.email;
    document.getElementById('pBio').value = userProfile.bio;

    editForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const data = new FormData(this);
      userProfile.name = data.get('name');
      userProfile.email = data.get('email');
      userProfile.bio = data.get('bio');
      renderProfileInfo();
      showToast('Profile updated successfully', 'success');
    });
  }

  const passForm = document.getElementById('changePasswordForm');
  if (passForm) {
    passForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const data = new FormData(this);
      const current = data.get('currentPassword');
      const newPass = data.get('newPassword');
      const confirm = data.get('confirmPassword');
      if (current !== userProfile.password) {
        showToast('Current password is incorrect', 'error');
        return;
      }
      if (newPass.length < 6) {
        showToast('New password must be at least 6 characters', 'error');
        return;
      }
      if (newPass !== confirm) {
        showToast('Passwords do not match', 'error');
        return;
      }
      userProfile.password = newPass;
      this.reset();
      showToast('Password changed successfully', 'success');
    });
  }

  renderProfileInfo();
}

function renderProfileInfo() {
  const info = document.getElementById('profileInfo');
  if (!info) return;
  const color = getAvatarColor(userProfile.name);
  info.innerHTML = `
    <div class="profile-header card">
      <div class="profile-avatar" style="background: ${color};">${userProfile.name.charAt(0)}</div>
      <div class="profile-info">
        <h2>${userProfile.name}</h2>
        <p>${userProfile.role} · ${userProfile.email}</p>
        <p style="font-size: 0.8rem; margin-top: 4px;">Member since ${userProfile.joinDate}</p>
      </div>
    </div>
  `;
}

// ===== LOGIN PAGE =====

function initLogin() {
  const form = document.getElementById('loginForm');
  if (!form) return;
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const data = new FormData(this);
    const username = data.get('username');
    const password = data.get('password');
    const errorEl = document.querySelector('.login-error');
    if (username === 'admin' && password === 'admin123') {
      window.location.href = 'dashboard.html';
    } else {
      if (errorEl) {
        errorEl.textContent = 'Invalid username or password';
        errorEl.classList.add('show');
      }
    }
  });
}

// ===== INIT =====

document.addEventListener('DOMContentLoaded', function () {
  initSidebar();
  initDarkMode();
  initNotificationBell();
  initAvatars();
  initLogin();

  const page = getPageName();

  if (page === 'dashboard') {
    renderDashboard();
  }

  if (page === 'students') {
    initStudents();
  }

  if (page === 'grades') {
    renderGrades();
  }

  if (page === 'attendance') {
    renderAttendance();
  }

  if (page === 'announcements') {
    initAnnouncements();
  }

  if (page === 'profile') {
    initProfile();
  }
});