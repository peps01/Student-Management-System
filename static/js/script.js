let userProfile = {};
let userRole = '';
let cachedAnnouncements = [];

function getAuthHeaders() {
  const stored = localStorage.getItem('smsUser');
  if (!stored) return {};
  const u = JSON.parse(stored);
  return { 'Authorization': 'Bearer ' + (u.token || '') };
}

const API = {
  async get(url) {
    const r = await fetch(url, { headers: { ...getAuthHeaders() } });
    if (!r.ok) throw new Error((await r.json()).error || 'Request failed');
    return r.json();
  },
  async post(url, body) {
    const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(body) });
    if (!r.ok) throw new Error((await r.json()).error || 'Request failed');
    return r.json();
  },
  async put(url, body) {
    const r = await fetch(url, { method: 'PUT', headers: { 'Content-Type': 'application/json', ...getAuthHeaders() }, body: JSON.stringify(body) });
    if (!r.ok) throw new Error((await r.json()).error || 'Request failed');
    return r.json();
  },
  async del(url) {
    const r = await fetch(url, { method: 'DELETE', headers: { ...getAuthHeaders() } });
    if (!r.ok) throw new Error((await r.json()).error || 'Request failed');
    return r.json();
  }
};

function getPageName() {
  const path = window.location.pathname;
  const parts = path.replace(/^\//, '').split('/');
  return parts.join('_');
}

function getGradeClass(score) {
  if (score >= 90) return 'grade-a';
  if (score >= 75) return 'grade-b';
  if (score >= 60) return 'grade-c';
  return 'grade-d';
}

const avatarColors = ['#3b82f6', '#8b5cf6', '#06b6d4', '#22c55e', '#f59e0b', '#ef4444', '#ec4899', '#14b8a6'];

function getAvatarColor(name) {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return avatarColors[Math.abs(hash) % avatarColors.length];
}

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

function openModal(id) { const el = document.getElementById(id); if (el) el.classList.add('show'); }
function closeModal(id) { const el = document.getElementById(id); if (el) el.classList.remove('show'); }

document.addEventListener('click', function (e) {
  if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('show');
});

function toggleDarkMode() {
  document.documentElement.classList.toggle('dark-mode');
  localStorage.setItem('darkMode', document.documentElement.classList.contains('dark-mode'));
  const btn = document.querySelector('.dark-mode-toggle');
  if (btn) btn.textContent = document.documentElement.classList.contains('dark-mode') ? '☀️' : '🌙';
}

function initDarkMode() {
  const btn = document.querySelector('.dark-mode-toggle');
  const isDark = document.documentElement.classList.contains('dark-mode');
  if (btn) { btn.textContent = isDark ? '☀️' : '🌙'; btn.addEventListener('click', toggleDarkMode); }
}

function initSidebar() {
  document.querySelectorAll('.hamburger').forEach(btn => {
    btn.addEventListener('click', () => { document.querySelector('.sidebar').classList.toggle('open'); });
  });
}

function initAvatars() {
  document.querySelectorAll('.user-avatar').forEach(el => {
    const name = el.getAttribute('data-name') || 'User';
    el.textContent = name.charAt(0).toUpperCase();
    el.style.background = getAvatarColor(name);
  });
}

// ======================== LOGIN ========================

function initLogin() {
  const form = document.getElementById('loginForm');
  if (!form) return;
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const data = new FormData(this);
    const errorEl = document.querySelector('.login-error');
    try {
      const res = await API.post('/api/login', { username: data.get('username'), password: data.get('password') });
      localStorage.setItem('smsUser', JSON.stringify(res));
      window.location.href = res.redirect || '/admin/dashboard';
    } catch {
      if (errorEl) { errorEl.textContent = 'Invalid username or password'; errorEl.classList.add('show'); }
    }
  });
}

// ======================== COMMON ========================

async function loadUserProfile() {
  const stored = localStorage.getItem('smsUser');
  if (!stored || !JSON.parse(stored).token) { window.location.href = '/login'; return; }
  const u = JSON.parse(stored);
  try {
    userProfile = await API.get('/api/profile');
  } catch {
    userProfile = u;
  }
  userRole = userProfile.role || u.role;
  const nameEl = document.getElementById('headerUserName');
  if (nameEl) nameEl.textContent = userProfile.name || u.name;
  document.querySelectorAll('.user-avatar').forEach(el => {
    const n = userProfile.name || u.name;
    el.textContent = n.charAt(0);
    el.style.background = getAvatarColor(n);
  });
}

async function logout() {
  try {
    await API.post('/api/logout');
  } catch {}
  localStorage.removeItem('smsUser');
  window.location.href = '/login';
}

document.addEventListener('click', function (e) {
  const logoutLink = e.target.closest('.sidebar-footer a');
  if (logoutLink) {
    e.preventDefault();
    logout();
  }
});

async function loadAnnouncements() {
  return API.get('/api/announcements');
}

function toggleBellDropdown(bell) {
  const dropdown = bell.querySelector('.bell-dropdown');
  if (!dropdown) return;
  const isOpen = dropdown.classList.contains('show');
  document.querySelectorAll('.bell-dropdown.show').forEach(d => d.classList.remove('show'));
  if (isOpen) return;
  dropdown.classList.add('show');
  if (!cachedAnnouncements.length) {
    dropdown.innerHTML = '<div class="bell-header">Notifications</div><div class="bell-empty">No notifications</div>';
    return;
  }
  dropdown.innerHTML = `<div class="bell-header">Notifications (${cachedAnnouncements.length})</div>
    ${cachedAnnouncements.slice().reverse().map(a => `
      <div class="bell-item">
        <div class="bell-item-title">${a.title}</div>
        <div class="bell-item-meta">${a.date}${a.author ? ' \u00b7 ' + a.author : ''}</div>
        <div style="font-size:0.8rem;color:var(--text-muted);margin-top:4px;line-height:1.4;">${a.body.length > 120 ? a.body.slice(0, 120) + '...' : a.body}</div>
      </div>
    `).join('')}`;
}

// ======================== ADMIN: DASHBOARD ========================

async function renderAdminDashboard() {
  const container = document.getElementById('adminDashboardContent');
  if (!container) return;
  try {
    const [stats, announcements] = await Promise.all([
      API.get('/api/dashboard/stats'),
      API.get('/api/announcements'),
    ]);
    const recent = announcements.slice(-3).reverse();
    container.innerHTML = `
      <div class="stat-cards">
        <div class="card stat-card"><div class="stat-icon blue">👥</div><div class="stat-info"><h3>${stats.total_students}</h3><p>Total Students</p></div></div>
        <div class="card stat-card"><div class="stat-icon green">👨‍🏫</div><div class="stat-info"><h3>${stats.total_faculties}</h3><p>Faculty</p></div></div>
        <div class="card stat-card"><div class="stat-icon yellow">📅</div><div class="stat-info"><h3>${stats.total_offerings}</h3><p>Class Offerings</p></div></div>
        <div class="card stat-card"><div class="stat-icon purple">📝</div><div class="stat-info"><h3>${stats.pending_enrollments}</h3><p>Pending Enrollments</p></div></div>
      </div>
      <div class="card" style="padding:22px;">
        <h3 style="font-size:1.05rem;margin-bottom:16px;">Recent Announcements</h3>
        ${recent.length ? recent.map(a => `<div style="padding:12px 0;border-bottom:1px solid var(--border);"><div style="display:flex;justify-content:space-between;align-items:center;"><strong>${a.title}</strong><span style="font-size:0.8rem;color:var(--text-muted);">${a.date}</span></div><p style="color:var(--text-muted);font-size:0.85rem;margin-top:4px;">${a.body.slice(0,100)}${a.body.length>100?'...':''}</p></div>`).join('') : '<p style="color:var(--text-muted);">No announcements yet.</p>'}
      </div>`;
  } catch (err) { showToast(err.message, 'error'); }
}

// ======================== ADMIN: DEPARTMENTS ========================

async function loadDepartments() {
  const data = await API.get('/api/departments');
  const table = document.getElementById('deptsTable');
  if (!table) return;
  table.innerHTML = `<thead><tr><th>Name</th><th>Code</th><th>Actions</th></tr></thead><tbody>
    ${data.map(d => `<tr><td><strong>${d.name}</strong></td><td>${d.code}</td><td><button class="btn btn-sm btn-primary" onclick="editDept(${d.id})">Edit</button> <button class="btn btn-sm btn-danger" onclick="deleteDept(${d.id})">Delete</button></td></tr>`).join('')}
  </tbody>`;
}

async function initDepartments() {
  await loadDepartments();
  document.getElementById('addDeptForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const fd = new FormData(this);
    try {
      await API.post('/api/departments', { name: fd.get('name'), code: fd.get('code') });
      await loadDepartments();
      closeModal('addDeptModal');
      this.reset();
      showToast('Department added', 'success');
    } catch (err) { showToast(err.message, 'error'); }
  });
  document.getElementById('editDeptForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const fd = new FormData(this);
    const id = fd.get('id');
    try {
      await API.put(`/api/departments/${id}`, { name: fd.get('name'), code: fd.get('code') });
      await loadDepartments();
      closeModal('editDeptModal');
      showToast('Department updated', 'success');
    } catch (err) { showToast(err.message, 'error'); }
  });
}

function editDept(id) {
  const table = document.getElementById('deptsTable');
  const row = table.querySelector(`tbody tr:nth-child(${id})`);
  API.get('/api/departments').then(depts => {
    const d = depts.find(x => x.id === id);
    if (!d) return;
    document.getElementById('editDeptId').value = d.id;
    document.getElementById('editDeptName').value = d.name;
    document.getElementById('editDeptCode').value = d.code;
    openModal('editDeptModal');
  });
}

async function deleteDept(id) {
  if (!confirm('Delete this department?')) return;
  try {
    await API.del(`/api/departments/${id}`);
    await loadDepartments();
    showToast('Department deleted', 'success');
  } catch (err) { showToast(err.message, 'error'); }
}

// ======================== ADMIN: COURSES ========================

async function loadCourses() {
  const [courses, depts] = await Promise.all([API.get('/api/courses'), API.get('/api/departments')]);
  const table = document.getElementById('coursesTable');
  if (!table) return;
  const deptOpts = () => depts.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
  table.innerHTML = `<thead><tr><th>Name</th><th>Code</th><th>Department</th><th>Actions</th></tr></thead><tbody>
    ${courses.map(c => `<tr><td><strong>${c.name}</strong></td><td>${c.code}</td><td>${c.department_name}</td><td><button class="btn btn-sm btn-primary" onclick="editCourse(${c.id})">Edit</button> <button class="btn btn-sm btn-danger" onclick="deleteCourse(${c.id})">Delete</button></td></tr>`).join('')}
  </tbody>`;
  ['addCourseDept', 'editCourseDept'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '<option value="">Select department</option>' + deptOpts();
  });
  window._courses = courses;
  window._depts = depts;
}

async function initCourses() {
  await loadCourses();
  document.getElementById('addCourseForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const fd = new FormData(this);
    try {
      await API.post('/api/courses', { name: fd.get('name'), code: fd.get('code'), department_id: parseInt(fd.get('department_id')) });
      await loadCourses();
      closeModal('addCourseModal');
      this.reset();
      showToast('Course added', 'success');
    } catch (err) { showToast(err.message, 'error'); }
  });
  document.getElementById('editCourseForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const fd = new FormData(this);
    const id = fd.get('id');
    try {
      await API.put(`/api/courses/${id}`, { name: fd.get('name'), code: fd.get('code'), department_id: parseInt(fd.get('department_id')) });
      await loadCourses();
      closeModal('editCourseModal');
      showToast('Course updated', 'success');
    } catch (err) { showToast(err.message, 'error'); }
  });
}

function editCourse(id) {
  const c = (window._courses || []).find(x => x.id === id);
  if (!c) return;
  document.getElementById('editCourseId').value = c.id;
  document.getElementById('editCourseName').value = c.name;
  document.getElementById('editCourseCode').value = c.code;
  document.getElementById('editCourseDept').value = c.department_id;
  openModal('editCourseModal');
}

async function deleteCourse(id) {
  if (!confirm('Delete this course?')) return;
  try { await API.del(`/api/courses/${id}`); await loadCourses(); showToast('Course deleted', 'success'); }
  catch (err) { showToast(err.message, 'error'); }
}

// ======================== ADMIN: SUBJECTS ========================

async function loadSubjects() {
  const [subjects, courses] = await Promise.all([API.get('/api/subjects'), API.get('/api/courses')]);
  const table = document.getElementById('subjectsTable');
  if (!table) return;
  const courseOpts = () => courses.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
  table.innerHTML = `<thead><tr><th>Name</th><th>Code</th><th>Course</th><th>Units</th><th>Actions</th></tr></thead><tbody>
    ${subjects.map(s => `<tr><td><strong>${s.name}</strong></td><td>${s.code}</td><td>${s.course_name}</td><td>${s.units}</td><td><button class="btn btn-sm btn-primary" onclick="editSubject(${s.id})">Edit</button> <button class="btn btn-sm btn-danger" onclick="deleteSubject(${s.id})">Delete</button></td></tr>`).join('')}
  </tbody>`;
  ['addSubjCourse', 'editSubjCourse'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '<option value="">Select course</option>' + courseOpts();
  });
  window._subjects = subjects;
  window._courses = courses;
}

async function initSubjects() {
  await loadSubjects();
  document.getElementById('addSubjectForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const fd = new FormData(this);
    try {
      await API.post('/api/subjects', { name: fd.get('name'), code: fd.get('code'), course_id: parseInt(fd.get('course_id')), units: parseInt(fd.get('units') || 3) });
      await loadSubjects();
      closeModal('addSubjectModal');
      this.reset();
      showToast('Subject added', 'success');
    } catch (err) { showToast(err.message, 'error'); }
  });
  document.getElementById('editSubjectForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const fd = new FormData(this);
    const id = fd.get('id');
    try {
      await API.put(`/api/subjects/${id}`, { name: fd.get('name'), code: fd.get('code'), course_id: parseInt(fd.get('course_id')), units: parseInt(fd.get('units') || 3) });
      await loadSubjects();
      closeModal('editSubjectModal');
      showToast('Subject updated', 'success');
    } catch (err) { showToast(err.message, 'error'); }
  });
}

function editSubject(id) {
  const s = (window._subjects || []).find(x => x.id === id);
  if (!s) return;
  document.getElementById('editSubjId').value = s.id;
  document.getElementById('editSubjName').value = s.name;
  document.getElementById('editSubjCode').value = s.code;
  document.getElementById('editSubjCourse').value = s.course_id;
  document.getElementById('editSubjUnits').value = s.units;
  openModal('editSubjectModal');
}

async function deleteSubject(id) {
  if (!confirm('Delete this subject?')) return;
  try { await API.del(`/api/subjects/${id}`); await loadSubjects(); showToast('Subject deleted', 'success'); }
  catch (err) { showToast(err.message, 'error'); }
}

// ======================== ADMIN: FACULTIES ========================

async function loadFaculties() {
  const [faculties, depts] = await Promise.all([API.get('/api/faculties'), API.get('/api/departments')]);
  const table = document.getElementById('facultiesTable');
  if (!table) return;
  const deptOpts = () => depts.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
  table.innerHTML = `<thead><tr><th>Name</th><th>Email</th><th>Username</th><th>Department</th><th>Actions</th></tr></thead><tbody>
    ${faculties.map(f => `<tr><td><strong>${f.name}</strong></td><td>${f.email}</td><td>${f.username}</td><td>${f.department_name}</td><td><button class="btn btn-sm btn-primary" onclick="editFaculty(${f.id})">Edit</button> <button class="btn btn-sm btn-danger" onclick="deleteFaculty(${f.id})">Delete</button></td></tr>`).join('')}
  </tbody>`;
  ['addFacDept', 'editFacDept'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '<option value="">Select department</option>' + deptOpts();
  });
  window._faculties = faculties;
}

async function initFaculties() {
  await loadFaculties();
  document.getElementById('addFacultyForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const fd = new FormData(this);
    try {
      const payload = { name: fd.get('name'), email: fd.get('email'), username: fd.get('username') || fd.get('email').split('@')[0].toLowerCase(), department_id: parseInt(fd.get('department_id')) };
      const res = await API.post('/api/faculties', payload);
      await loadFaculties();
      closeModal('addFacultyModal');
      this.reset();
      showToast(`Faculty added. Username: ${payload.username}, Password: faculty123`, 'success');
    } catch (err) { showToast(err.message, 'error'); }
  });
  document.getElementById('editFacultyForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const fd = new FormData(this);
    const id = fd.get('id');
    try {
      await API.put(`/api/faculties/${id}`, { name: fd.get('name'), email: fd.get('email'), department_id: parseInt(fd.get('department_id')) });
      await loadFaculties();
      closeModal('editFacultyModal');
      showToast('Faculty updated', 'success');
    } catch (err) { showToast(err.message, 'error'); }
  });
}

function editFaculty(id) {
  const f = (window._faculties || []).find(x => x.id === id);
  if (!f) return;
  document.getElementById('editFacId').value = f.id;
  document.getElementById('editFacName').value = f.name;
  document.getElementById('editFacEmail').value = f.email;
  document.getElementById('editFacDept').value = f.department_id;
  openModal('editFacultyModal');
}

async function deleteFaculty(id) {
  if (!confirm('Delete this faculty?')) return;
  try { await API.del(`/api/faculties/${id}`); await loadFaculties(); showToast('Faculty deleted', 'success'); }
  catch (err) { showToast(err.message, 'error'); }
}

// ======================== ADMIN: SECTIONS ========================

async function loadSections() {
  const data = await API.get('/api/sections');
  const table = document.getElementById('sectionsTable');
  if (!table) return;
  table.innerHTML = `<thead><tr><th>Name</th><th style="text-align:right;">Actions</th></tr></thead><tbody>
    ${data.map(s => `<tr><td><strong>${s.name}</strong></td><td style="text-align:right;"><button class="btn btn-sm btn-primary" onclick="editSection(${s.id})">Edit</button> <button class="btn btn-sm btn-danger" onclick="deleteSection(${s.id})">Delete</button></td></tr>`).join('')}
  </tbody>`;
  window._sections = data;
}

async function initSections() {
  await loadSections();
  document.getElementById('addSectionForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const fd = new FormData(this);
    try {
      await API.post('/api/sections', { name: fd.get('name') });
      await loadSections();
      closeModal('addSectionModal');
      this.reset();
      showToast('Section added', 'success');
    } catch (err) { showToast(err.message, 'error'); }
  });
  document.getElementById('editSectionForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const fd = new FormData(this);
    const id = fd.get('id');
    try {
      await API.put(`/api/sections/${id}`, { name: fd.get('name') });
      await loadSections();
      closeModal('editSectionModal');
      showToast('Section updated', 'success');
    } catch (err) { showToast(err.message, 'error'); }
  });
}

function editSection(id) {
  const s = (window._sections || []).find(x => x.id === id);
  if (!s) return;
  document.getElementById('editSectionId').value = s.id;
  document.getElementById('editSectionName').value = s.name;
  openModal('editSectionModal');
}

async function deleteSection(id) {
  if (!confirm('Delete this section?')) return;
  try { await API.del(`/api/sections/${id}`); await loadSections(); showToast('Section deleted', 'success'); }
  catch (err) { showToast(err.message, 'error'); }
}

// ======================== ADMIN: OFFERINGS ========================

async function loadOfferings() {
  const [offerings, subjects, faculties, sections] = await Promise.all([
    API.get('/api/offerings'), API.get('/api/subjects'), API.get('/api/faculties'), API.get('/api/sections')
  ]);
  const table = document.getElementById('offeringsTable');
  if (!table) return;
  const subjOpts = () => subjects.map(s => `<option value="${s.id}">${s.code} - ${s.name}</option>`).join('');
  const facOpts = () => faculties.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
  const secOpts = () => sections.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
  const sectionFilter = `<div style="margin-bottom:12px;"><select id="sectionFilter" onchange="filterOfferingsBySection()" class="form-control" style="max-width:250px;"><option value="">All Sections</option>${sections.map(s => `<option value="${s.id}">${s.name}</option>`).join('')}</select></div>`;
  const existing = document.getElementById('sectionFilterWrap');
  if (!existing) {
    const wrap = document.createElement('div');
    wrap.id = 'sectionFilterWrap';
    wrap.innerHTML = sectionFilter;
    table.parentElement.insertBefore(wrap, table);
  }
  table.innerHTML = `<thead><tr><th>Subject</th><th>Section</th><th>Schedule</th><th>Faculty</th><th>Semester</th><th>School Year</th><th>Actions</th></tr></thead><tbody>
    ${offerings.map(o => `<tr data-section-id="${o.section_id}"><td><strong>${o.subject_name}</strong></td><td>${o.section_name}</td><td>${o.schedule}</td><td>${o.faculty_name}</td><td>${o.semester}</td><td>${o.school_year}</td><td><button class="btn btn-sm btn-primary" onclick="editOffering(${o.id})">Edit</button> <button class="btn btn-sm btn-danger" onclick="deleteOffering(${o.id})">Delete</button></td></tr>`).join('')}
  </tbody>`;
  ['addOffSubject', 'editOffSubject'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '<option value="">Select subject</option>' + subjOpts();
  });
  ['addOffSection', 'editOffSection'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '<option value="">Select section</option>' + secOpts();
  });
  ['addOffFaculty', 'editOffFaculty'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '<option value="">Select faculty</option>' + facOpts();
  });
  window._offerings = offerings;
  window._subjects = subjects;
  window._faculties = faculties;
  window._sections = sections;
}

function filterOfferingsBySection() {
  const val = document.getElementById('sectionFilter')?.value;
  document.querySelectorAll('#offeringsTable tbody tr').forEach(row => {
    row.style.display = !val || row.dataset.sectionId === val ? '' : 'none';
  });
}

async function initOfferings() {
  await loadOfferings();
  document.getElementById('addOfferingForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const fd = new FormData(this);
    try {
      await API.post('/api/offerings', {
        subject_id: parseInt(fd.get('subject_id')), section_id: parseInt(fd.get('section_id')),
        schedule: fd.get('schedule'), faculty_id: parseInt(fd.get('faculty_id')),
        semester: fd.get('semester'), school_year: fd.get('school_year')
      });
      await loadOfferings();
      closeModal('addOfferingModal');
      this.reset();
      showToast('Offering created', 'success');
    } catch (err) { showToast(err.message, 'error'); }
  });
  document.getElementById('editOfferingForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const fd = new FormData(this);
    const id = fd.get('id');
    try {
      await API.put(`/api/offerings/${id}`, {
        subject_id: parseInt(fd.get('subject_id')), section_id: parseInt(fd.get('section_id')),
        schedule: fd.get('schedule'), faculty_id: parseInt(fd.get('faculty_id')),
        semester: fd.get('semester'), school_year: fd.get('school_year')
      });
      await loadOfferings();
      closeModal('editOfferingModal');
      showToast('Offering updated', 'success');
    } catch (err) { showToast(err.message, 'error'); }
  });
}

function editOffering(id) {
  const o = (window._offerings || []).find(x => x.id === id);
  if (!o) return;
  document.getElementById('editOffId').value = o.id;
  document.getElementById('editOffSubject').value = o.subject_id;
  document.getElementById('editOffSection').value = o.section_id;
  document.getElementById('editOffSchedule').value = o.schedule;
  document.getElementById('editOffFaculty').value = o.faculty_id;
  document.getElementById('editOffSemester').value = o.semester;
  document.getElementById('editOffSchoolYear').value = o.school_year;
  openModal('editOfferingModal');
}

async function deleteOffering(id) {
  if (!confirm('Delete this offering?')) return;
  try { await API.del(`/api/offerings/${id}`); await loadOfferings(); showToast('Offering deleted', 'success'); }
  catch (err) { showToast(err.message, 'error'); }
}

// ======================== ADMIN: STUDENTS ========================

let studentsData = [];
let currentPage = 1;
const perPage = 8;
let sortState = { field: null, asc: true };

function sortData(data) {
  if (!sortState.field) return data;
  const f = sortState.field;
  const sign = sortState.asc ? 1 : -1;
  return [...data].sort((a, b) => {
    let va = a[f], vb = b[f];
    if (f === 'year' || f === 'id') return sign * (va - vb);
    va = String(va).toLowerCase(); vb = String(vb).toLowerCase();
    return va < vb ? -sign : va > vb ? sign : 0;
  });
}

function sortArrow(field) {
  if (sortState.field !== field) return '<span class="sort-arrow">↕</span>';
  return `<span class="sort-arrow">${sortState.asc ? '▲' : '▼'}</span>`;
}

function sortableHeader(label, field) {
  const active = sortState.field === field ? ' active' : '';
  return `<th class="sortable${active}" onclick="setSort('${field}')">${label} ${sortArrow(field)}</th>`;
}

function setSort(field) {
  if (sortState.field === field) sortState.asc = !sortState.asc;
  else { sortState.field = field; sortState.asc = true; }
  renderStudents(document.getElementById('studentSearch')?.value);
}

function paginateData(data) {
  const totalPages = Math.ceil(data.length / perPage) || 1;
  if (currentPage > totalPages) currentPage = totalPages;
  const start = (currentPage - 1) * perPage;
  return data.slice(start, start + perPage);
}

function renderPagination(totalItems) {
  const container = document.getElementById('paginationControls');
  if (!container) return;
  const totalPages = Math.ceil(totalItems / perPage) || 1;
  if (totalPages <= 1) { container.innerHTML = ''; return; }
  let html = `<button class="page-btn" onclick="goToPage(${currentPage - 1})" ${currentPage <= 1 ? 'disabled' : ''}>&laquo; Prev</button>`;
  for (let i = 1; i <= totalPages; i++) {
    html += `<button class="page-btn${i === currentPage ? ' active' : ''}" onclick="goToPage(${i})">${i}</button>`;
  }
  html += `<button class="page-btn" onclick="goToPage(${currentPage + 1})" ${currentPage >= totalPages ? 'disabled' : ''}>Next &raquo;</button>`;
  html += `<span class="page-info">${totalItems} total</span>`;
  container.innerHTML = html;
}

function goToPage(page) {
  currentPage = page;
  renderStudents(document.getElementById('studentSearch')?.value);
}

async function loadStudents() {
  const students = await API.get('/api/students');
  studentsData = students.map(s => ({ ...s, _sections: s.section_name || '' }));
  return studentsData;
}

function renderStudents(filter) {
  const table = document.getElementById('studentsTable');
  if (!table) return;
  let list = studentsData;
  if (filter) {
    const q = filter.toLowerCase();
    list = studentsData.filter(s => s.name.toLowerCase().includes(q) || s.email.toLowerCase().includes(q) || (s.student_number && s.student_number.toLowerCase().includes(q)));
  }
  const sorted = sortData(list);
  const pageData = paginateData(sorted);
  renderPagination(sorted.length);

  let html = `<thead><tr>${sortableHeader('Student #', 'student_number')}${sortableHeader('Name', 'name')}${sortableHeader('Email', 'email')}${sortableHeader('Course', 'course_name')}${sortableHeader('Year', 'year')}<th>Sections</th><th>Actions</th></tr></thead><tbody>`;
  if (!pageData.length) {
    html += `<tr><td colspan="7"><div class="empty-state"><div class="empty-icon">📭</div><p>No students found</p></div></td></tr>`;
  } else {
    pageData.forEach(s => {
      html += `<tr><td>${s.student_number}</td><td><strong>${s.name}</strong></td><td>${s.email}</td><td>${s.course_name}</td><td>Year ${s.year}</td><td style="font-size:0.85rem;">${s._sections || '<span style="color:var(--text-muted);">—</span>'}</td><td><button class="btn btn-sm btn-primary" onclick="editStudent(${s.id})">Edit</button> <button class="btn btn-sm btn-danger" onclick="deleteStudent(${s.id})">Delete</button></td></tr>`;
    });
  }
  html += `</tbody>`;
  table.innerHTML = html;
}

async function initStudentsPage() {
  await loadStudents();
  const [courses, sections] = await Promise.all([
    API.get('/api/courses'),
    API.get('/api/sections')
  ]);
  const courseOpts = () => courses.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
  ['addCourse', 'editCourse'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '<option value="">Select course</option>' + courseOpts();
  });
  const sectionOpts = () => sections.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
  ['addSection', 'editSection'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '<option value="">No section</option>' + sectionOpts();
  });
  const searchInput = document.getElementById('studentSearch');
  if (searchInput) searchInput.addEventListener('input', function () { currentPage = 1; renderStudents(this.value); });
  renderStudents('');

  document.getElementById('addStudentForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const fd = new FormData(this);
    const payload = {
      student_number: fd.get('student_number'), name: fd.get('name'), email: fd.get('email'),
      course_id: parseInt(fd.get('course_id')), year: parseInt(fd.get('year'))
    };
    const secVal = fd.get('section_id');
    if (secVal) payload.section_id = parseInt(secVal);
    try {
      const res = await API.post('/api/students', payload);
      await loadStudents();
      renderStudents(document.getElementById('studentSearch').value);
      closeModal('addStudentModal');
      this.reset();
      showToast(`Student added. Username: ${res.username}, Password: ${res.password}`, 'success');
    } catch (err) { showToast(err.message, 'error'); }
  });

  document.getElementById('editStudentForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const fd = new FormData(this);
    const id = parseInt(fd.get('id'));
    const payload = {
      name: fd.get('name'), email: fd.get('email'),
      course_id: parseInt(fd.get('course_id')), year: parseInt(fd.get('year'))
    };
    const secVal = fd.get('section_id');
    payload.section_id = secVal ? parseInt(secVal) : null;
    try {
      await API.put(`/api/students/${id}`, payload);
      await loadStudents();
      renderStudents(document.getElementById('studentSearch').value);
      closeModal('editStudentModal');
      showToast('Student updated', 'success');
    } catch (err) { showToast(err.message, 'error'); }
  });
}

function editStudent(id) {
  const s = studentsData.find(x => x.id === id);
  if (!s) return;
  document.getElementById('editId').value = s.id;
  document.getElementById('editName').value = s.name;
  document.getElementById('editEmail').value = s.email;
  document.getElementById('editCourse').value = s.course_id;
  document.getElementById('editYear').value = s.year;
  if (document.getElementById('editSection')) document.getElementById('editSection').value = s.section_id || '';
  openModal('editStudentModal');
}

async function deleteStudent(id) {
  if (!confirm('Delete this student?')) return;
  try { await API.del(`/api/students/${id}`); await loadStudents(); renderStudents(document.getElementById('studentSearch')?.value); showToast('Student deleted', 'success'); }
  catch (err) { showToast(err.message, 'error'); }
}

// ======================== ADMIN: ENROLLMENTS ========================

let enrollmentFilter = 'All';

async function loadEnrollments() {
  const status = enrollmentFilter === 'All' ? '' : enrollmentFilter;
  const url = status ? `/api/enrollments?status=${status}` : '/api/enrollments';
  const data = await API.get(url);
  const table = document.getElementById('enrollmentsTable');
  if (!table) return;
  table.innerHTML = `<thead><tr><th>Student</th><th>Student #</th><th>Subjects</th><th>Status</th><th>Date</th><th>Actions</th></tr></thead><tbody>
    ${data.length ? data.map(e => `<tr>
      <td><strong>${e.student_name}</strong></td><td>${e.student_number}</td>
      <td>${(e.items || []).map(i => i.subject_name).join(', ')}</td>
      <td><span class="badge ${e.status === 'Approved' ? 'badge-success' : e.status === 'Rejected' ? 'badge-danger' : 'badge-warning'}">${e.status}</span></td>
      <td>${e.date}</td>
      <td>${e.status === 'Pending' ? `<button class="btn btn-sm btn-success" onclick="approveEnrollment(${e.id})">Approve</button> <button class="btn btn-sm btn-danger" onclick="rejectEnrollment(${e.id})">Reject</button>` : '<span style="color:var(--text-muted);font-size:0.85rem;">Done</span>'}</td>
    </tr>`).join('') : `<tr><td colspan="7"><div class="empty-state"><div class="empty-icon">📭</div><p>No enrollments found</p></div></td></tr>`}
  </tbody>`;
}

function filterEnrollments(status) {
  enrollmentFilter = status;
  loadEnrollments();
  document.querySelectorAll('.page-header .btn-ghost').forEach(b => b.classList.remove('btn-primary'));
  const btn = document.getElementById(`filter${status}`);
  if (btn) { btn.classList.remove('btn-ghost'); btn.classList.add('btn-primary'); }
}

async function initEnrollments() {
  filterEnrollments('Pending');
}

async function approveEnrollment(id) {
  try { await API.put(`/api/enrollments/${id}/approve`); await loadEnrollments(); showToast('Enrollment approved', 'success'); }
  catch (err) { showToast(err.message, 'error'); }
}

async function rejectEnrollment(id) {
  try { await API.put(`/api/enrollments/${id}/reject`); await loadEnrollments(); showToast('Enrollment rejected', 'success'); }
  catch (err) { showToast(err.message, 'error'); }
}

// ======================== ADMIN: GRADES OVERVIEW ========================

async function initAdminGrades() {
  const offerings = await API.get('/api/offerings');
  const sel = document.getElementById('adminGradeOffering');
  if (sel) sel.innerHTML = '<option value="">Select offering</option>' + offerings.map(o => `<option value="${o.id}">${o.subject_name} - ${o.section_name} (${o.schedule})</option>`).join('');
}

async function loadAdminGrades() {
  const sel = document.getElementById('adminGradeOffering');
  const oid = parseInt(sel?.value);
  if (!oid) { showToast('Please select an offering', 'error'); return; }
  const container = document.getElementById('adminGradesContainer');
  if (!container) return;
  const grades = await API.get(`/api/reports/grades?offering_id=${oid}`);
  if (!grades.students || !grades.students.length) {
    container.innerHTML = '<div class="empty-state"><div class="empty-icon">📊</div><p>No grades found for this offering</p></div>';
    return;
  }
  let html = `<div class="table-container"><table><thead><tr><th>Student</th><th>Prelim</th><th>Midterm</th><th>Final</th><th>Final Grade</th><th>Status</th></tr></thead><tbody>`;
  grades.students.forEach(g => {
    html += `<tr><td><strong>${g.student_name}</strong></td><td class="${getGradeClass(g.prelim)}">${g.prelim}</td><td class="${getGradeClass(g.midterm)}">${g.midterm}</td><td class="${getGradeClass(g.final)}">${g.final}</td><td><strong class="${getGradeClass(g.final_grade)}">${g.final_grade}</strong></td><td><span class="badge ${g.grade_status === 'Passed' ? 'badge-success' : 'badge-danger'}">${g.grade_status}</span></td></tr>`;
  });
  html += `</tbody></table></div>`;
  html += `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-top:24px;">
    <div class="card" style="padding:18px;"><p style="color:var(--text-muted);font-size:0.8rem;margin-bottom:4px;">Average Grade</p><h3 class="${getGradeClass(grades.average)}">${grades.average}%</h3></div>
    <div class="card" style="padding:18px;"><p style="color:var(--text-muted);font-size:0.8rem;margin-bottom:4px;">Passing Rate</p><h3 style="color:var(--success);">${grades.passing_rate}%</h3></div>
    <div class="card" style="padding:18px;"><p style="color:var(--text-muted);font-size:0.8rem;margin-bottom:4px;">Students</p><h3>${grades.students.length}</h3></div>
  </div>`;
  container.innerHTML = html;
}

// ======================== ADMIN: ATTENDANCE OVERVIEW ========================

async function initAdminAttendance() {
  const offerings = await API.get('/api/offerings');
  const sel = document.getElementById('adminAttOffering');
  if (sel) sel.innerHTML = '<option value="">Select offering</option>' + offerings.map(o => `<option value="${o.id}">${o.subject_name} - ${o.section_name}</option>`).join('');
}

async function loadAdminAttendance() {
  const sel = document.getElementById('adminAttOffering');
  const oid = parseInt(sel?.value);
  if (!oid) { showToast('Please select an offering', 'error'); return; }
  const container = document.getElementById('adminAttendanceContainer');
  if (!container) return;
  const data = await API.get(`/api/reports/attendance?offering_id=${oid}`);
  if (!data.students || !data.students.length) {
    container.innerHTML = '<div class="empty-state"><div class="empty-icon">📋</div><p>No attendance records found</p></div>';
    return;
  }
  let html = `<p style="margin-bottom:12px;color:var(--text-muted);">Total Sessions: ${data.total_sessions}</p>`;
  html += `<div class="table-container"><table><thead><tr><th>Student</th><th>Total</th><th>Present</th><th>Absent</th><th>Percentage</th></tr></thead><tbody>`;
  data.students.forEach(s => {
    html += `<tr><td><strong>${s.student_name}</strong></td><td>${s.total}</td><td style="color:var(--success);font-weight:600;">${s.present}</td><td style="color:var(--danger);font-weight:600;">${s.absent}</td><td><span class="badge ${s.percentage >= 80 ? 'badge-success' : s.percentage >= 60 ? 'badge-warning' : 'badge-danger'}">${s.percentage}%</span></td></tr>`;
  });
  html += `</tbody></table></div>`;
  container.innerHTML = html;
}

// ======================== ADMIN: ANNOUNCEMENTS ========================

let announcementsData = [];

async function loadAnnouncementsList() {
  announcementsData = await API.get('/api/announcements');
  const container = document.getElementById('announcementsList');
  if (!container) return;
  if (!announcementsData.length) {
    container.innerHTML = '<div class="empty-state"><div class="empty-icon">📢</div><p>No announcements yet</p></div>';
    return;
  }
  container.innerHTML = [...announcementsData].reverse().map(a => `
    <div class="card announcement-card">
      <div class="annc-header"><span class="annc-title">${a.title}</span><span class="annc-meta">${a.date}</span></div>
      <div class="annc-body">${a.body}</div>
      <div class="annc-author"><span class="author-avatar">${a.author.charAt(0)}</span>Posted by ${a.author}</div>
    </div>
  `).join('');
}

async function initAnnouncementsPage() {
  await loadAnnouncementsList();
  document.getElementById('announcementForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const fd = new FormData(this);
    const title = fd.get('title').trim();
    const body = fd.get('body').trim();
    if (!title || !body) return;
    const now = new Date();
    const dateStr = now.toISOString().slice(0, 16).replace('T', ' ');
    try {
      await API.post('/api/announcements', { title, body, date: dateStr });
      await loadAnnouncementsList();
      closeModal('addAnnouncementModal');
      this.reset();
      showToast('Announcement posted', 'success');
    } catch (err) { showToast(err.message, 'error'); }
  });
}

// ======================== ADMIN: REPORTS ========================

async function initReports() {
  const [enrollmentReport, offerings] = await Promise.all([
    API.get('/api/reports/enrollment'),
    API.get('/api/offerings')
  ]);

  const cardContainer = document.getElementById('enrollmentReportCards');
  if (cardContainer) {
    cardContainer.innerHTML = `
      <div class="card stat-card"><div class="stat-icon blue">📝</div><div class="stat-info"><h3>${enrollmentReport.total}</h3><p>Total Enrollments</p></div></div>
      <div class="card stat-card"><div class="stat-icon green">✅</div><div class="stat-info"><h3>${enrollmentReport.approved}</h3><p>Approved</p></div></div>
      <div class="card stat-card"><div class="stat-icon yellow">⏳</div><div class="stat-info"><h3>${enrollmentReport.pending}</h3><p>Pending</p></div></div>
      <div class="card stat-card"><div class="stat-icon red">❌</div><div class="stat-info"><h3>${enrollmentReport.rejected}</h3><p>Rejected</p></div></div>
    `;
  }

  const content = document.getElementById('enrollmentReportContent');
  if (content) {
    content.innerHTML = '<h4 style="margin-bottom:8px;">Course Distribution</h4>';
    if (enrollmentReport.course_distribution && enrollmentReport.course_distribution.length) {
      const maxCount = Math.max(...enrollmentReport.course_distribution.map(c => c.count), 1);
      content.innerHTML += enrollmentReport.course_distribution.map(c =>
        `<div class="bar-row"><span class="bar-label">${c.name}</span><div class="bar-track"><div class="bar-fill blue" style="width:${(c.count/maxCount)*100}%"></div></div><span class="bar-value">${c.count}</span></div>`
      ).join('');
    } else {
      content.innerHTML += '<p style="color:var(--text-muted);">No data available.</p>';
    }
  }

  const offeringOpts = () => offerings.map(o => `<option value="${o.id}">${o.subject_name} - ${o.section}</option>`).join('');
  ['reportOfferingSelect', 'gradeReportOfferingSelect'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '<option value="">Select offering</option>' + offeringOpts();
  });
}

async function loadAttendanceReport() {
  const sel = document.getElementById('reportOfferingSelect');
  const oid = parseInt(sel?.value);
  if (!oid) { showToast('Select an offering', 'error'); return; }
  const data = await API.get(`/api/reports/attendance?offering_id=${oid}`);
  const container = document.getElementById('attendanceReportContent');
  if (!container) return;
  if (!data.students || !data.students.length) {
    container.innerHTML = '<p style="color:var(--text-muted);">No data available.</p>';
    return;
  }
  let html = `<div class="table-container"><table><thead><tr><th>Student</th><th>Total</th><th>Present</th><th>Absent</th><th>%</th></tr></thead><tbody>`;
  data.students.forEach(s => {
    html += `<tr><td>${s.student_name}</td><td>${s.total}</td><td style="color:var(--success)">${s.present}</td><td style="color:var(--danger)">${s.absent}</td><td><span class="badge ${s.percentage >= 80 ? 'badge-success' : s.percentage >= 60 ? 'badge-warning' : 'badge-danger'}">${s.percentage}%</span></td></tr>`;
  });
  html += `</tbody></table></div>`;
  container.innerHTML = html;
}

async function loadGradeReport() {
  const sel = document.getElementById('gradeReportOfferingSelect');
  const oid = parseInt(sel?.value);
  if (!oid) { showToast('Select an offering', 'error'); return; }
  const data = await API.get(`/api/reports/grades?offering_id=${oid}`);
  const container = document.getElementById('gradeReportContent');
  if (!container) return;
  if (!data.students || !data.students.length) {
    container.innerHTML = '<p style="color:var(--text-muted);">No data available.</p>';
    return;
  }
  let html = `<div class="table-container"><table><thead><tr><th>Student</th><th>Prelim</th><th>Midterm</th><th>Final</th><th>Final Grade</th><th>Status</th></tr></thead><tbody>`;
  data.students.forEach(g => {
    html += `<tr><td>${g.student_name}</td><td class="${getGradeClass(g.prelim)}">${g.prelim}</td><td class="${getGradeClass(g.midterm)}">${g.midterm}</td><td class="${getGradeClass(g.final)}">${g.final}</td><td><strong class="${getGradeClass(g.final_grade)}">${g.final_grade}</strong></td><td><span class="badge ${g.grade_status === 'Passed' ? 'badge-success' : 'badge-danger'}">${g.grade_status}</span></td></tr>`;
  });
  html += `</tbody></table></div>`;
  html += `<div style="margin-top:16px;"><strong>Average: </strong><span class="${getGradeClass(data.average)}">${data.average}%</span> &nbsp; <strong>Passing Rate: </strong><span style="color:var(--success);">${data.passing_rate}%</span></div>`;
  container.innerHTML = html;
}

// ======================== FACULTY: DASHBOARD ========================

async function renderFacultyDashboard() {
  const container = document.getElementById('facultyDashboardContent');
  if (!container) return;
  try {
    const stored = JSON.parse(localStorage.getItem('smsUser') || '{}');
    const profile = await API.get('/api/profile');
    const facultyId = profile.faculty_id || stored.faculty_id;
    if (!facultyId) { container.innerHTML = '<div class="card" style="padding:40px;text-align:center;"><p style="color:var(--text-muted);">Faculty profile not found. Please contact the administrator.</p></div>'; return; }
    const offerings = await API.get(`/api/offerings/faculty/${facultyId}`);
    const totalStudents = offerings.reduce((sum, o) => sum + (o.enrolled_count || 0), 0);
    const grouped = {};
    offerings.forEach(o => {
      const key = o.section_name || 'Unassigned';
      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(o);
    });
    const sectionKeys = Object.keys(grouped).sort();
    container.innerHTML = `
      <div class="stat-cards">
        <div class="card stat-card"><div class="stat-icon blue">📚</div><div class="stat-info"><h3>${offerings.length}</h3><p>Assigned Classes</p></div></div>
        <div class="card stat-card"><div class="stat-icon green">👥</div><div class="stat-info"><h3>${totalStudents}</h3><p>Total Students</p></div></div>
      </div>
      ${sectionKeys.map(section => `
        <div class="card" style="padding:18px;margin-bottom:16px;">
          <h3 style="font-size:1rem;margin-bottom:14px;display:flex;align-items:center;gap:8px;">📋 ${section} <span class="badge badge-info" style="font-size:0.75rem;">${grouped[section].length} class${grouped[section].length !== 1 ? 'es' : ''}</span></h3>
          ${grouped[section].map(o => `
            <div style="padding:12px;border:1px solid var(--border);border-radius:var(--radius);margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
              <div><strong>${o.subject_name}</strong><br><span style="color:var(--text-muted);font-size:0.85rem;">${o.schedule} | Enrolled: ${o.enrolled_count}</span></div>
              <div style="display:flex;gap:8px;">
                <a href="/faculty/attendance/${o.id}" class="btn btn-sm btn-primary">Attendance</a>
                <a href="/faculty/grades/${o.id}" class="btn btn-sm btn-success">Grades</a>
              </div>
            </div>
          `).join('')}
        </div>
      `).join('') || '<div class="card" style="padding:22px;"><p style="color:var(--text-muted);">No classes assigned yet.</p></div>'}
    `;
  } catch (err) { container.innerHTML = `<div class="card" style="padding:40px;text-align:center;"><p style="color:var(--text-muted);">Error loading data: ${err.message}</p></div>`; }
}

// ======================== FACULTY: CLASSES ========================

async function renderFacultyClasses() {
  const container = document.getElementById('facultyClassesContent');
  if (!container) return;
  try {
    const stored = JSON.parse(localStorage.getItem('smsUser') || '{}');
    const profile = await API.get('/api/profile');
    const facultyId = profile.faculty_id || stored.faculty_id;
    if (!facultyId) { container.innerHTML = '<div class="card" style="padding:40px;text-align:center;"><p style="color:var(--text-muted);">Faculty profile not found. Please contact the administrator.</p></div>'; return; }
    const offerings = await API.get(`/api/offerings/faculty/${facultyId}`);
    let html = `<p style="margin-bottom:16px;color:var(--text-muted);">You have <strong>${offerings.length}</strong> assigned class${offerings.length !== 1 ? 'es' : ''} this semester.</p>`;
    html += `<div style="margin-bottom:20px;"><input type="text" id="classSearchInput" class="form-control" placeholder="Search by subject, code, section, or schedule..." style="max-width:450px;" oninput="filterFacultyClasses()"></div>`;
    html += `<div id="facultyClassCards">`;
    if (offerings.length) {
      offerings.forEach(o => {
        html += `<div class="card" style="padding:20px;margin-bottom:16px;" data-search="${o.subject_name} ${o.subject_code} ${o.section_name} ${o.schedule}">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
            <div style="flex:1;min-width:200px;">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
                <h3 style="margin:0;">${o.subject_name}</h3>
                <span class="badge badge-info" style="font-size:0.75rem;padding:2px 8px;">${o.subject_code}</span>
              </div>
              <p style="color:var(--text-muted);font-size:0.85rem;margin-bottom:6px;">Section: ${o.section_name}</p>
              <div style="display:flex;flex-wrap:wrap;gap:14px;font-size:0.85rem;color:var(--text-muted);">
                <span>📅 ${o.schedule}</span>
                <span>🏫 ${o.semester} ${o.school_year}</span>
              </div>
            </div>
            <div style="text-align:right;min-width:130px;">
              <div style="font-size:1.6rem;font-weight:700;color:var(--primary);line-height:1.2;">${o.enrolled_count}</div>
              <div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:10px;">Enrolled</div>
              <div style="display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end;">
                <a href="/faculty/attendance/${o.id}" class="btn btn-sm btn-primary">📋 Attendance</a>
                <a href="/faculty/grades/${o.id}" class="btn btn-sm btn-success">📊 Grades</a>
                <button class="btn btn-sm btn-ghost" onclick="viewClassRoster(${o.id})">👥 Roster</button>
              </div>
            </div>
          </div>
        </div>`;
      });
    } else {
      html += '<div class="card" style="padding:40px;text-align:center;color:var(--text-muted);"><p>No classes assigned to you yet.</p></div>';
    }
    html += `</div>`;
    container.innerHTML = html;
  } catch (err) { container.innerHTML = `<div class="card" style="padding:40px;text-align:center;"><p style="color:var(--text-muted);">Error loading data: ${err.message}</p></div>`; }
}

function filterFacultyClasses() {
  const q = document.getElementById('classSearchInput')?.value.toLowerCase() || '';
  document.querySelectorAll('#facultyClassCards .card').forEach(card => {
    card.style.display = card.dataset.search.toLowerCase().includes(q) ? '' : 'none';
  });
}

async function viewClassRoster(offeringId) {
  try {
    const data = await API.get(`/api/attendance?offering_id=${offeringId}`);
    const tbody = document.getElementById('rosterModalBody');
    if (!tbody) return;
    document.getElementById('rosterModalTitle').textContent = `Class Roster`;
    if (!data.length) {
      tbody.innerHTML = '<tr><td colspan="2"><div class="empty-state"><p>No enrolled students found</p></div></td></tr>';
    } else {
      tbody.innerHTML = data.map((s, i) => `<tr><td style="width:40px;color:var(--text-muted);">${i + 1}</td><td><strong>${s.student_name}</strong></td></tr>`).join('');
    }
    document.getElementById('rosterModal').classList.add('show');
  } catch (err) { showToast(err.message, 'error'); }
}

// ======================== FACULTY: ATTENDANCE ========================

async function initFacultyAttendance() {
  const pathParts = window.location.pathname.split('/');
  const offeringId = parseInt(pathParts[pathParts.length - 1]);
  if (!offeringId) return;
  try {
    const o = await API.get(`/api/offerings/${offeringId}`);
    const titleEl = document.getElementById('attClassTitle');
    if (titleEl && o) titleEl.textContent = `Attendance: ${o.subject_name} - ${o.section_name}`;

    const today = new Date().toISOString().slice(0, 10);
    const dateInput = document.getElementById('attDate');
    if (dateInput) dateInput.value = today;

    window._facultyOfferingId = offeringId;
  } catch (err) { showToast(err.message, 'error'); }
}

async function loadAttendanceForDate() {
  const oid = window._facultyOfferingId;
  const date = document.getElementById('attDate')?.value;
  if (!oid || !date) { showToast('Select a date', 'error'); return; }
  const table = document.getElementById('facultyAttTable');
  if (!table) return;
  const data = await API.get(`/api/attendance?offering_id=${oid}`);
  table.innerHTML = `<thead><tr><th>Student</th><th>Status</th><th>Action</th></tr></thead><tbody>`;
  if (!data.length) {
    table.innerHTML += `<tr><td colspan="3"><div class="empty-state"><p>No enrolled students found</p></div></td></tr>`;
    return;
  }
  data.forEach(s => {
    const existing = (s.records || []).find(r => r.date === date);
    const status = existing ? existing.status : '';
    table.innerHTML += `<tr data-student-id="${s.student_id}">
      <td><strong>${s.student_name}</strong></td>
      <td><span class="badge ${status === 'Present' ? 'badge-success' : status === 'Absent' ? 'badge-danger' : 'badge-warning'}">${status || 'Not marked'}</span></td>
      <td>
        <button class="btn btn-sm btn-success" onclick="markStudentAttendance(${s.student_id}, 'Present')">Present</button>
        <button class="btn btn-sm btn-danger" onclick="markStudentAttendance(${s.student_id}, 'Absent')">Absent</button>
      </td>
    </tr>`;
  });
}

async function markStudentAttendance(studentId, status) {
  const oid = window._facultyOfferingId;
  const date = document.getElementById('attDate')?.value;
  if (!oid || !date) return;
  try {
    await API.post('/api/attendance/mark', { offering_id: oid, student_id: studentId, date, status });
    await loadAttendanceForDate();
    showToast(`Marked ${status}`, 'success');
  } catch (err) { showToast(err.message, 'error'); }
}

async function markAllPresent() {
  const table = document.getElementById('facultyAttTable');
  if (!table) return;
  const rows = table.querySelectorAll('tbody tr[data-student-id]');
  if (!rows.length) { showToast('No students loaded', 'error'); return; }
  const oid = window._facultyOfferingId;
  const date = document.getElementById('attDate')?.value;
  if (!oid || !date) { showToast('Select a date first', 'error'); return; }
  let count = 0;
  for (const row of rows) {
    const sid = parseInt(row.dataset.studentId);
    try {
      await API.post('/api/attendance/mark', { offering_id: oid, student_id: sid, date, status: 'Present' });
      count++;
    } catch {}
  }
  showToast(`Marked ${count} student(s) Present`, 'success');
  await loadAttendanceForDate();
}

// ======================== FACULTY: GRADES ========================

async function initFacultyGrades() {
  const pathParts = window.location.pathname.split('/');
  const offeringId = parseInt(pathParts[pathParts.length - 1]);
  if (!offeringId) return;
  try {
    const o = await API.get(`/api/offerings/${offeringId}`);
    const titleEl = document.getElementById('gradeClassTitle');
    if (titleEl && o) titleEl.textContent = `Grades: ${o.subject_name} - ${o.section_name}`;

    const grades = await API.get(`/api/grades?offering_id=${offeringId}`);
    const table = document.getElementById('facultyGradesTable');
    if (!table) return;
    table.innerHTML = `<thead><tr><th>Student</th><th>Prelim</th><th>Midterm</th><th>Final</th><th>Final Grade</th><th>Status</th><th>Actions</th></tr></thead><tbody>`;
    if (!grades.length) {
      table.innerHTML += `<tr><td colspan="7"><div class="empty-state"><p>No students found</p></div></td></tr>`;
      return;
    }
    grades.forEach(g => {
      const fg = g.final_grade || ((g.prelim + g.midterm + g.final) / 3).toFixed(2);
      table.innerHTML += `<tr>
        <td><strong>${g.student_name}</strong></td>
        <td><input type="number" class="form-control" style="width:80px;" value="${g.prelim}" min="0" max="100" id="prelim_${g.student_id}"></td>
        <td><input type="number" class="form-control" style="width:80px;" value="${g.midterm}" min="0" max="100" id="midterm_${g.student_id}"></td>
        <td><input type="number" class="form-control" style="width:80px;" value="${g.final}" min="0" max="100" id="final_${g.student_id}"></td>
        <td><strong class="${getGradeClass(fg)}">${fg}</strong></td>
        <td><span class="badge ${g.grade_status === 'Passed' ? 'badge-success' : 'badge-danger'}">${g.grade_status}</span></td>
        <td><button class="btn btn-sm btn-primary" onclick="saveGrade(${offeringId}, ${g.student_id})">Save</button></td>
      </tr>`;
    });
    table.innerHTML += `</tbody>`;
    window._facultyGradesOfferingId = offeringId;
  } catch (err) { showToast(err.message, 'error'); }
}

async function saveGrade(offeringId, studentId) {
  const prelim = parseFloat(document.getElementById(`prelim_${studentId}`)?.value || 0);
  const midterm = parseFloat(document.getElementById(`midterm_${studentId}`)?.value || 0);
  const final = parseFloat(document.getElementById(`final_${studentId}`)?.value || 0);
  try {
    await API.put(`/api/grades/${offeringId}/${studentId}`, { prelim, midterm, final });
    showToast('Grade saved', 'success');
    await initFacultyGrades();
  } catch (err) { showToast(err.message, 'error'); }
}

// ======================== STUDENT: DASHBOARD ========================

async function renderStudentDashboard() {
  const container = document.getElementById('studentDashboardContent');
  if (!container) return;
  try {
    const stored = JSON.parse(localStorage.getItem('smsUser') || '{}');
    const profile = await API.get('/api/profile');
    const sid = profile.student_id;
    if (!sid) { container.innerHTML = '<p>Student profile not found.</p>'; return; }

    const [grades, attSummary, dash] = await Promise.all([
      API.get(`/api/grades/student/${sid}`),
      API.get(`/api/attendance/summary/${sid}`),
      API.get('/api/dashboard/student').catch(() => null)
    ]);

    const avgGrade = grades.length ? grades.reduce((s, g) => s + g.final_grade, 0) / grades.length : 0;
    const passed = grades.filter(g => g.grade_status === 'Passed').length;

    let subjectsHtml = '';
    if (dash && dash.subjects && dash.subjects.length) {
      const grouped = {};
      dash.subjects.forEach(s => {
        const key = s.section_name || 'Other';
        if (!grouped[key]) grouped[key] = [];
        grouped[key].push(s);
      });
      subjectsHtml = Object.keys(grouped).sort().map(section => `
        <div class="card" style="padding:18px;margin-bottom:16px;">
          <h3 style="font-size:1rem;margin-bottom:12px;display:flex;align-items:center;gap:8px;">📋 ${section} <span class="badge badge-info" style="font-size:0.75rem;">${grouped[section].length} subject${grouped[section].length !== 1 ? 's' : ''}</span></h3>
          ${grouped[section].map(s => `
            <div style="padding:10px 0;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;">
              <span><strong>${s.subject_name}</strong> — ${s.schedule || ''}</span>
              <span style="color:var(--text-muted);font-size:0.85rem;">${s.faculty_name || ''}</span>
            </div>
          `).join('')}
        </div>
      `).join('');
    }

    container.innerHTML = `
      <div class="stat-cards">
        <div class="card stat-card"><div class="stat-icon blue">📚</div><div class="stat-info"><h3>${grades.length}</h3><p>Subjects</p></div></div>
        <div class="card stat-card"><div class="stat-icon green">📊</div><div class="stat-info"><h3 class="${getGradeClass(avgGrade)}">${avgGrade.toFixed(1)}%</h3><p>Average Grade</p></div></div>
        <div class="card stat-card"><div class="stat-icon yellow">✅</div><div class="stat-info"><h3>${passed}/${grades.length}</h3><p>Passed</p></div></div>
        <div class="card stat-card"><div class="stat-icon purple">📋</div><div class="stat-info"><h3>${attSummary.percentage || 0}%</h3><p>Attendance Rate</p></div></div>
      </div>
      ${subjectsHtml}
      <div class="charts-row">
        <div class="card chart-card">
          <h4>My Grades</h4>
          ${grades.length ? `<div class="table-container"><table><thead><tr><th>Subject</th><th>Final Grade</th><th>Status</th></tr></thead><tbody>
            ${grades.map(g => `<tr><td>${g.subject_name}</td><td><strong class="${getGradeClass(g.final_grade)}">${g.final_grade}</strong></td><td><span class="badge ${g.grade_status === 'Passed' ? 'badge-success' : 'badge-danger'}">${g.grade_status}</span></td></tr>`).join('')}
          </tbody></table></div>` : '<p style="color:var(--text-muted);">No grades yet.</p>'}
        </div>
        <div class="card chart-card">
          <h4>Attendance Summary</h4>
          <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:calc(100% - 34px);gap:12px;">
            <div style="
              width:130px;height:130px;border-radius:50%;
              background:conic-gradient(var(--success) 0deg ${(attSummary.percentage||0)/100*360}deg, var(--danger) ${(attSummary.percentage||0)/100*360}deg 360deg);
              position:relative;flex-shrink:0;
            ">
              <div style="
                position:absolute;top:50%;left:50%;
                transform:translate(-50%,-50%);
                width:76px;height:76px;border-radius:50%;
                background:var(--card-bg);
                display:flex;flex-direction:column;
                align-items:center;justify-content:center;
              ">
                <strong style="font-size:1.2rem;">${attSummary.percentage || 0}%</strong>
                <small style="color:var(--text-muted);font-size:0.7rem;">Rate</small>
              </div>
            </div>
            <div style="display:flex;gap:20px;font-size:0.85rem;">
              <span><span style="color:var(--success);">●</span> Present: <strong>${attSummary.present || 0}</strong></span>
              <span><span style="color:var(--danger);">●</span> Absent: <strong>${attSummary.absent || 0}</strong></span>
            </div>
          </div>
        </div>
      </div>
    `;
  } catch (err) { showToast(err.message, 'error'); }
}

// ======================== STUDENT: ENROLLMENT ========================

let selectedOfferingIds = [];
let studentId = null;

async function initStudentEnrollment() {
  try {
    const profile = await API.get('/api/profile');
    studentId = profile.student_id;
    if (!studentId) { showToast('Student profile not found', 'error'); return; }

    const [offerings, enrollments] = await Promise.all([
      API.get('/api/offerings?course_id=' + profile.course_id),
      API.get(`/api/enrollments/student/${studentId}`)
    ]);

    // Show enrollment history
    const historyContainer = document.getElementById('enrollmentHistory');
    if (historyContainer) {
      if (enrollments.length) {
        historyContainer.innerHTML = `<div class="table-container"><table><thead><tr><th>Date</th><th>Subjects</th><th>Status</th></tr></thead><tbody>
          ${enrollments.map(e => `<tr><td>${e.date}</td><td>${(e.items || []).map(i => i.subject_name).join(', ')}</td><td><span class="badge ${e.status === 'Approved' ? 'badge-success' : e.status === 'Rejected' ? 'badge-danger' : 'badge-warning'}">${e.status}</span></td></tr>`).join('')}
        </tbody></table></div>`;
      } else {
        historyContainer.innerHTML = '<p style="color:var(--text-muted);">No enrollments yet.</p>';
      }
    }

    // Show available offerings
    const container = document.getElementById('availableOfferings');
    if (!container) return;

    const enrolledOids = new Set();
    enrollments.filter(e => e.status === 'Approved' || e.status === 'Pending').forEach(e => {
      (e.items || []).forEach(i => enrolledOids.add(i.offering_id));
    });

    const available = offerings.filter(o => !enrolledOids.has(o.id));

    if (!available.length) {
      container.innerHTML = '<p style="color:var(--text-muted);">No available offerings for enrollment.</p>';
      return;
    }

    const uniqueSections = [...new Set(available.map(o => o.section_name).filter(Boolean))].sort();
    let html = '';
    if (uniqueSections.length > 1) {
      html += `<div style="margin-bottom:12px;"><select id="enrollSectionFilter" class="form-control" style="max-width:250px;" onchange="filterEnrollOfferings()"><option value="">All Sections</option>${uniqueSections.map(s => `<option value="${s}">${s}</option>`).join('')}</select></div>`;
    }
    html += `<div id="enrollOfferingsList">`;
    html += available.map(o => `
      <label class="card enroll-card" style="padding:16px;display:flex;align-items:center;gap:12px;cursor:pointer;margin-bottom:8px;" data-section="${o.section_name || ''}">
        <input type="checkbox" class="offering-checkbox" value="${o.id}" onchange="toggleOffering(${o.id})">
        <div>
          <strong>${o.subject_name}</strong> (${o.subject_code})
          <p style="color:var(--text-muted);font-size:0.85rem;">${o.section_name} | ${o.schedule} | ${o.faculty_name}</p>
        </div>
      </label>
    `).join('');
    html += `</div>`;
    container.innerHTML = html;
  } catch (err) { showToast(err.message, 'error'); }
}

function toggleOffering(id) {
  const idx = selectedOfferingIds.indexOf(id);
  if (idx > -1) selectedOfferingIds.splice(idx, 1);
  else selectedOfferingIds.push(id);
  const btn = document.getElementById('submitEnrollmentBtn');
  if (btn) btn.disabled = selectedOfferingIds.length === 0;
}

function filterEnrollOfferings() {
  const val = document.getElementById('enrollSectionFilter')?.value?.toLowerCase() || '';
  document.querySelectorAll('#enrollOfferingsList .enroll-card').forEach(card => {
    card.style.display = !val || (card.dataset.section || '').toLowerCase() === val ? '' : 'none';
  });
}

async function submitEnrollment() {
  if (!studentId || !selectedOfferingIds.length) return;
  try {
    await API.post('/api/enrollments', { student_id: studentId, offering_ids: selectedOfferingIds });
    showToast('Enrollment submitted! Awaiting approval.', 'success');
    selectedOfferingIds = [];
    document.getElementById('submitEnrollmentBtn').disabled = true;
    await initStudentEnrollment();
  } catch (err) { showToast(err.message, 'error'); }
}

// ======================== STUDENT: GRADES ========================

async function renderStudentGrades() {
  const container = document.getElementById('studentGradesContent');
  if (!container) return;
  try {
    const profile = await API.get('/api/profile');
    const sid = profile.student_id;
    if (!sid) { container.innerHTML = '<p>Student profile not found.</p>'; return; }
    const grades = await API.get(`/api/grades/student/${sid}`);
    if (!grades.length) {
      container.innerHTML = '<div class="empty-state"><div class="empty-icon">📊</div><p>No grades available yet.</p></div>';
      return;
    }
    container.innerHTML = `<div class="table-container"><table><thead><tr><th>Subject</th><th>Prelim</th><th>Midterm</th><th>Final</th><th>Final Grade</th><th>Status</th></tr></thead><tbody>
      ${grades.map(g => `<tr><td><strong>${g.subject_name}</strong></td><td class="${getGradeClass(g.prelim)}">${g.prelim}</td><td class="${getGradeClass(g.midterm)}">${g.midterm}</td><td class="${getGradeClass(g.final)}">${g.final}</td><td><strong class="${getGradeClass(g.final_grade)}">${g.final_grade}</strong></td><td><span class="badge ${g.grade_status === 'Passed' ? 'badge-success' : 'badge-danger'}">${g.grade_status}</span></td></tr>`).join('')}
    </tbody></table></div>`;
  } catch (err) { showToast(err.message, 'error'); }
}

// ======================== STUDENT: ATTENDANCE ========================

async function renderStudentAttendance() {
  const container = document.getElementById('studentAttendanceContent');
  if (!container) return;
  try {
    const profile = await API.get('/api/profile');
    const sid = profile.student_id;
    if (!sid) { container.innerHTML = '<p>Student profile not found.</p>'; return; }
    const summary = await API.get(`/api/attendance/summary/${sid}`);
    container.innerHTML = `
      <div class="stat-cards" style="margin-bottom:20px;">
        <div class="card stat-card"><div class="stat-icon green">✅</div><div class="stat-info"><h3>${summary.present || 0}</h3><p>Present</p></div></div>
        <div class="card stat-card"><div class="stat-icon red">❌</div><div class="stat-info"><h3>${summary.absent || 0}</h3><p>Absent</p></div></div>
        <div class="card stat-card"><div class="stat-icon purple">📊</div><div class="stat-info"><h3>${summary.percentage || 0}%</h3><p>Attendance Rate</p></div></div>
      </div>
      <div class="card" style="padding:20px;">
        <h4 style="margin-bottom:12px;">Attendance Breakdown</h4>
        <div style="height:24px;background:var(--bg);border-radius:6px;overflow:hidden;display:flex;">
          ${summary.total ? `<div style="width:${summary.percentage}%;background:var(--success);transition:width 0.8s;"></div><div style="width:${100 - summary.percentage}%;background:var(--danger);transition:width 0.8s;"></div>` : '<div style="width:100%;background:var(--bg);"></div>'}
        </div>
        <div style="display:flex;gap:20px;margin-top:8px;font-size:0.85rem;">
          <span><span style="color:var(--success);">●</span> Present: ${summary.present || 0}</span>
          <span><span style="color:var(--danger);">●</span> Absent: ${summary.absent || 0}</span>
          <span>Total: ${summary.total || 0}</span>
        </div>
      </div>
    `;
  } catch (err) { showToast(err.message, 'error'); }
}

// ======================== PROFILE PAGE ========================

async function loadProfile() {
  userProfile = await API.get('/api/profile');
}

function buildProfileSidebar() {
  const nav = document.getElementById('profileSidebar');
  if (!nav) return;
  const role = userProfile.role || userRole;
  let brand = 'SMS';
  if (role === 'Administrator') { brand = 'SMS Admin'; }
  else if (role === 'Faculty')  { brand = 'SMS Faculty'; }
  else                          { brand = 'SMS Student'; }
  const brandEl = document.querySelector('.sidebar-brand span');
  if (brandEl) brandEl.textContent = brand;

  let links = '';
  if (role === 'Administrator') {
    links = `<div class="nav-section">Academic Setup</div>
      <a href="/admin/dashboard"><span class="nav-icon">📊</span> Dashboard</a>
      <a href="/admin/departments"><span class="nav-icon">🏛️</span> Departments</a>
      <a href="/admin/courses"><span class="nav-icon">📚</span> Courses</a>
      <a href="/admin/subjects"><span class="nav-icon">📖</span> Subjects</a>
      <a href="/admin/faculties"><span class="nav-icon">👨‍🏫</span> Faculties</a>
      <a href="/admin/sections"><span class="nav-icon">📋</span> Sections</a>
      <a href="/admin/offerings"><span class="nav-icon">📅</span> Class Offerings</a>
      <div class="nav-section">Management</div>
      <a href="/admin/students"><span class="nav-icon">👥</span> Students</a>
      <a href="/admin/enrollments"><span class="nav-icon">📝</span> Enrollments</a>
      <a href="/admin/grades"><span class="nav-icon">📊</span> Grades</a>
      <a href="/admin/attendance"><span class="nav-icon">📋</span> Attendance</a>
      <a href="/admin/announcements"><span class="nav-icon">📢</span> Announcements</a>
      <a href="/admin/reports"><span class="nav-icon">📈</span> Reports</a>
      <div class="nav-section">Account</div>
      <a href="/profile" class="active"><span class="nav-icon">👤</span> Profile</a>`;
  } else if (role === 'Faculty') {
    links = `<div class="nav-section">Main</div>
      <a href="/faculty/dashboard"><span class="nav-icon">📊</span> Dashboard</a>
      <a href="/faculty/classes"><span class="nav-icon">📚</span> My Classes</a>
      <div class="nav-section">Account</div>
      <a href="/profile" class="active"><span class="nav-icon">👤</span> Profile</a>`;
  } else {
    links = `<div class="nav-section">Main</div>
      <a href="/student/dashboard"><span class="nav-icon">📊</span> Dashboard</a>
      <a href="/student/enrollment"><span class="nav-icon">📝</span> Enrollment</a>
      <a href="/student/grades"><span class="nav-icon">📊</span> My Grades</a>
      <a href="/student/attendance"><span class="nav-icon">📋</span> Attendance</a>
      <div class="nav-section">Account</div>
      <a href="/profile" class="active"><span class="nav-icon">👤</span> Profile</a>`;
  }
  nav.innerHTML = links;
}

async function initProfilePage() {
  await loadProfile();
  buildProfileSidebar();
  renderProfileInfo();

  const editForm = document.getElementById('editProfileForm');
  if (editForm) {
    document.getElementById('pName').value = userProfile.name;
    document.getElementById('pEmail').value = userProfile.email;
    document.getElementById('pBio').value = userProfile.bio || '';
    editForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const fd = new FormData(this);
      try {
        await API.put('/api/profile', { name: fd.get('name'), email: fd.get('email'), bio: fd.get('bio') });
        await loadProfile();
        renderProfileInfo();
        showToast('Profile updated', 'success');
      } catch (err) { showToast(err.message, 'error'); }
    });
  }

  const passForm = document.getElementById('changePasswordForm');
  if (passForm) {
    passForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const fd = new FormData(this);
      const payload = { currentPassword: fd.get('currentPassword'), newPassword: fd.get('newPassword'), confirmPassword: fd.get('confirmPassword') };
      if (payload.newPassword.length < 6) { showToast('Password must be at least 6 characters', 'error'); return; }
      if (payload.newPassword !== payload.confirmPassword) { showToast('Passwords do not match', 'error'); return; }
      try {
        await API.put('/api/profile/password', payload);
        this.reset();
        showToast('Password changed', 'success');
      } catch (err) { showToast(err.message, 'error'); }
    });
  }
}

function renderProfileInfo() {
  const info = document.getElementById('profileInfo');
  if (!info) return;
  const color = getAvatarColor(userProfile.name);
  info.innerHTML = `
    <div class="profile-header card">
      <div class="profile-avatar" style="background:${color};">${userProfile.name.charAt(0)}</div>
      <div class="profile-info">
        <h2>${userProfile.name}</h2>
        <p>${userProfile.role} · ${userProfile.email}</p>
        ${userProfile.student_number ? `<p style="font-size:0.85rem;">Student #: ${userProfile.student_number} | ${userProfile.course_name} - Year ${userProfile.year}</p>` : ''}
        <p style="font-size:0.8rem;margin-top:4px;">Member since ${userProfile.joinDate}</p>
      </div>
    </div>
  `;
}

// ======================== INIT DISPATCHER ========================

document.addEventListener('DOMContentLoaded', function () {
  initSidebar();
  initDarkMode();
  initAvatars();
  initLogin();

  const page = getPageName();

  if (page !== 'login') {
    loadUserProfile();
    loadAnnouncements().then(anns => {
      cachedAnnouncements = anns;
      const badge = document.querySelector('.bell-badge');
      if (badge) badge.textContent = anns.length;
    });
    document.querySelectorAll('.notification-bell').forEach(bell => {
      bell.addEventListener('click', function (e) {
        e.stopPropagation();
        toggleBellDropdown(this);
      });
    });
    document.addEventListener('click', () => {
      document.querySelectorAll('.bell-dropdown.show').forEach(d => d.classList.remove('show'));
    });
  }

  // Admin pages
  if (page === 'admin_dashboard') renderAdminDashboard();
  else if (page === 'admin_departments') initDepartments();
  else if (page === 'admin_courses') initCourses();
  else if (page === 'admin_subjects') initSubjects();
  else if (page === 'admin_faculties') initFaculties();
  else if (page === 'admin_offerings') initOfferings();
  else if (page === 'admin_students') initStudentsPage();
  else if (page === 'admin_enrollments') initEnrollments();
  else if (page === 'admin_grades') { initAdminGrades(); }
  else if (page === 'admin_attendance') { initAdminAttendance(); }
  else if (page === 'admin_announcements') initAnnouncementsPage();
  else if (page === 'admin_sections') initSections();
  else if (page === 'admin_reports') initReports();
  // Faculty pages
  else if (page === 'faculty_dashboard') renderFacultyDashboard();
  else if (page === 'faculty_classes') renderFacultyClasses();
  else if (page.startsWith('faculty_attendance')) initFacultyAttendance();
  else if (page.startsWith('faculty_grades')) initFacultyGrades();
  // Student pages
  else if (page === 'student_dashboard') renderStudentDashboard();
  else if (page === 'student_enrollment') initStudentEnrollment();
  else if (page === 'student_grades') renderStudentGrades();
  else if (page === 'student_attendance') renderStudentAttendance();
  // Profile
  else if (page === 'profile') initProfilePage();
});
