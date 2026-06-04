let userProfile = {};
let userRole = '';

function getAuthHeaders() {
  const stored = localStorage.getItem('smsUser');
  if (!stored) return {};
  const u = JSON.parse(stored);
  return { 'X-Username': u.username };
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
  }
};

function getPageName() {
  const path = window.location.pathname;
  const parts = path.replace(/^\//, '').split('/');
  return parts.join('_');
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

// ======================== LOGOUT ========================

function initLogout() {
  const link = document.getElementById('logoutLink');
  if (!link) return;
  link.addEventListener('click', function (e) {
    e.preventDefault();
    localStorage.removeItem('smsUser');
    window.location.href = '/login';
  });
}

// ======================== REGISTER ========================

function initRegister() {
  const form = document.getElementById('registerForm');
  if (!form) return;
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const data = new FormData(this);
    const errorEl = document.querySelector('.login-error');
    try {
      const res = await API.post('/api/register', {
        username: data.get('username'),
        name: data.get('name'),
        email: data.get('email'),
        password: data.get('password'),
      });
      showToast('Account created! Redirecting to login...', 'success');
      setTimeout(() => { window.location.href = '/login'; }, 1500);
    } catch (err) {
      if (errorEl) { errorEl.textContent = err.message; errorEl.classList.add('show'); }
    }
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
      window.location.href = res.redirect || '/dashboard';
    } catch {
      if (errorEl) { errorEl.textContent = 'Invalid username or password'; errorEl.classList.add('show'); }
    }
  });
}

// ======================== COMMON ========================

async function loadUserProfile() {
  const stored = localStorage.getItem('smsUser');
  if (!stored) { window.location.href = '/login'; return; }
  const u = JSON.parse(stored);
  userProfile = u;
  userRole = u.role;
  const nameEl = document.getElementById('headerUserName');
  if (nameEl) nameEl.textContent = u.name;
  document.querySelectorAll('.user-avatar').forEach(el => {
    const n = u.name;
    el.textContent = n.charAt(0);
    el.style.background = getAvatarColor(n);
  });
}

// ======================== DASHBOARD ========================

async function renderDashboard() {
  const container = document.getElementById('dashboardContent');
  if (!container) return;
  try {
    const stats = await API.get('/api/dashboard/stats');
    container.innerHTML = `
      <div class="stat-cards">
        <div class="card stat-card"><div class="stat-icon blue">👥</div><div class="stat-info"><h3>${stats.total_students}</h3><p>Total Students</p></div></div>
        <div class="card stat-card"><div class="stat-icon green">👨‍🏫</div><div class="stat-info"><h3>${stats.total_faculties}</h3><p>Faculty</p></div></div>
        <div class="card stat-card"><div class="stat-icon yellow">📅</div><div class="stat-info"><h3>${stats.total_offerings}</h3><p>Class Offerings</p></div></div>
        <div class="card stat-card"><div class="stat-icon purple">📝</div><div class="stat-info"><h3>${stats.pending_enrollments}</h3><p>Pending Enrollments</p></div></div>
      </div>
      <div class="card" style="padding:22px;">
        <h3 style="font-size:1.05rem;margin-bottom:16px;">Welcome to the Dashboard</h3>
        <p style="color:var(--text-muted);font-size:0.9rem;line-height:1.6;">
          This is your admin dashboard. Use the sidebar to navigate through the system. 
          You can manage students, enrollments, and view important metrics at a glance.
        </p>
      </div>`;
  } catch (err) { showToast(err.message, 'error'); }
}

// ======================== INIT DISPATCHER ========================

document.addEventListener('DOMContentLoaded', function () {
  initSidebar();
  initDarkMode();
  initAvatars();
  initLogin();
  initRegister();
  initLogout();

  const page = getPageName();

  if (page !== 'login' && page !== 'register') {
    loadUserProfile();
  }

  if (page === 'dashboard') renderDashboard();
});
