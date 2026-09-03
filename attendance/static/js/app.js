/* =====================================================
   HOD–Teacher Attendance System — App JS
   ===================================================== */

'use strict';

// ── Auto-dismiss toasts ────────────────────────────────
function initToasts() {
  document.querySelectorAll('.toast-alert').forEach(function (el) {
    var btn = el.querySelector('.toast-close');
    if (btn) btn.addEventListener('click', function () { dismissToast(el); });
    setTimeout(function () { dismissToast(el); }, 4500);
  });
}

function dismissToast(el) {
  if (!el.parentNode) return;
  el.style.transition = 'opacity .3s, transform .3s';
  el.style.opacity = '0';
  el.style.transform = 'translateX(110%)';
  setTimeout(function () { if (el.parentNode) el.remove(); }, 320);
}

// ── Sidebar toggle (mobile) ────────────────────────────
function initSidebar() {
  var toggle  = document.getElementById('sidebar-toggle');
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('sidebar-overlay');

  if (!toggle || !sidebar) return;

  function openSidebar() {
    sidebar.classList.add('open');
    if (overlay) { overlay.classList.add('show'); overlay.removeAttribute('aria-hidden'); }
    toggle.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    if (overlay) { overlay.classList.remove('show'); overlay.setAttribute('aria-hidden', 'true'); }
    toggle.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }

  function isMobile() { return window.innerWidth <= 768; }

  toggle.addEventListener('click', function () {
    if (isMobile()) {
      sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
    }
  });

  if (overlay) overlay.addEventListener('click', closeSidebar);

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && sidebar.classList.contains('open')) closeSidebar();
  });

  // Close on nav link click (mobile only)
  sidebar.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () {
      if (isMobile()) closeSidebar();
    });
  });

  // Restore on resize to desktop
  window.addEventListener('resize', function () {
    if (!isMobile()) {
      sidebar.classList.remove('open');
      if (overlay) { overlay.classList.remove('show'); }
      document.body.style.overflow = '';
    }
  });
}

// ── Active sidebar link ────────────────────────────────
function initActiveNav() {
  var path = window.location.pathname;
  var links = document.querySelectorAll('.sidebar-nav a');
  var bestMatch = null;
  var bestLen = 0;
  links.forEach(function (a) {
    var href = a.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href) && href.length > bestLen) {
      bestLen = href.length;
      bestMatch = a;
    }
  });
  if (bestMatch) bestMatch.classList.add('active');
}

// ── Confirm delete ─────────────────────────────────────
function initConfirmDelete() {
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      var msg = el.getAttribute('data-confirm') || 'Are you sure you want to delete this?';
      if (!confirm(msg)) e.preventDefault();
    });
  });
}

// ── Attendance: Present All / Absent All ───────────────
function initAttendanceBulk() {
  var presentAll = document.getElementById('btn-present-all');
  var absentAll  = document.getElementById('btn-absent-all');

  if (presentAll) {
    presentAll.addEventListener('click', function () {
      document.querySelectorAll('.att-radio-present').forEach(function (r) {
        r.checked = true; updateRowHighlight(r);
      });
    });
  }

  if (absentAll) {
    absentAll.addEventListener('click', function () {
      document.querySelectorAll('.att-radio-absent').forEach(function (r) {
        r.checked = true; updateRowHighlight(r);
      });
    });
  }

  document.querySelectorAll('.att-radio-present, .att-radio-absent').forEach(function (r) {
    r.addEventListener('change', function () { updateRowHighlight(r); });
  });
}

function updateRowHighlight(radio) {
  var row = radio.closest('tr');
  if (!row) return;
  row.classList.remove('att-row-present', 'att-row-absent');
  if (radio.checked) {
    row.classList.add(radio.value === 'Present' ? 'att-row-present' : 'att-row-absent');
  }
}

// ── Live table search ──────────────────────────────────
function initTableSearch() {
  var input = document.getElementById('table-search');
  if (!input) return;
  input.addEventListener('input', function () {
    var q = this.value.toLowerCase().trim();
    document.querySelectorAll('.searchable-row').forEach(function (row) {
      row.style.display = (!q || row.textContent.toLowerCase().includes(q)) ? '' : 'none';
    });
  });
}

// ── Percentage bar fill ────────────────────────────────
function initPctBars() {
  document.querySelectorAll('.pct-fill').forEach(function (bar) {
    var pct = parseFloat(bar.getAttribute('data-pct') || '0');
    bar.style.width = Math.min(Math.max(pct, 0), 100) + '%';
    bar.classList.remove('low', 'medium');
    if (pct < 50) bar.classList.add('low');
    else if (pct < 75) bar.classList.add('medium');
  });
}

// ── Set today as default on date inputs ────────────────
function initDateDefaults() {
  var today = new Date().toISOString().split('T')[0];
  document.querySelectorAll('input[type="date"][data-today]').forEach(function (el) {
    if (!el.value) el.value = today;
  });
}

// ── Topbar live date ───────────────────────────────────
function initTopbarDate() {
  var el = document.querySelector('.topbar-date');
  if (!el) return;
  var d = new Date();
  el.textContent = d.toLocaleDateString('en-IN', {
    weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
  });
}
// ── Initial row highlights (attendance page) ───────────
function initRowHighlights() {
  document.querySelectorAll('.att-radio-present:checked, .att-radio-absent:checked').forEach(function (r) {
    updateRowHighlight(r);
  });
}

// ── Boot ───────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  initToasts();
  initSidebar();
  initActiveNav();
  initConfirmDelete();
  initAttendanceBulk();
  initTableSearch();
  initPctBars();
  initDateDefaults();
  initTopbarDate();
  initRowHighlights();
});
