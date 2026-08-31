/* =====================================================
   HOD–Teacher Attendance System — App JS
   ===================================================== */

'use strict';

// ── Auto-dismiss toasts ────────────────────────────────
function initToasts() {
  document.querySelectorAll('.toast-alert').forEach(function (el) {
    // Close button
    var btn = el.querySelector('.toast-close');
    if (btn) {
      btn.addEventListener('click', function () {
        dismissToast(el);
      });
    }
    // Auto dismiss after 4 seconds
    setTimeout(function () {
      dismissToast(el);
    }, 4000);
  });
}

function dismissToast(el) {
  el.style.transition = 'opacity .3s, transform .3s';
  el.style.opacity = '0';
  el.style.transform = 'translateX(100%)';
  setTimeout(function () { el.remove(); }, 320);
}

// ── Sidebar toggle (mobile) ────────────────────────────
function initSidebar() {
  var toggle = document.querySelector('.topbar-toggle');
  var sidebar = document.querySelector('.sidebar');
  var overlay = document.querySelector('.sidebar-overlay');

  if (!toggle || !sidebar) return;

  toggle.addEventListener('click', function () {
    sidebar.classList.toggle('open');
    if (overlay) overlay.classList.toggle('show');
  });

  if (overlay) {
    overlay.addEventListener('click', function () {
      sidebar.classList.remove('open');
      overlay.classList.remove('show');
    });
  }
}

// ── Confirm delete dialogs ─────────────────────────────
function initConfirmDelete() {
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      var msg = el.getAttribute('data-confirm') || 'Are you sure you want to delete this?';
      if (!confirm(msg)) {
        e.preventDefault();
        return false;
      }
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
        r.checked = true;
        updateRowHighlight(r);
      });
    });
  }

  if (absentAll) {
    absentAll.addEventListener('click', function () {
      document.querySelectorAll('.att-radio-absent').forEach(function (r) {
        r.checked = true;
        updateRowHighlight(r);
      });
    });
  }

  // Row highlight on toggle change
  document.querySelectorAll('.att-radio-present, .att-radio-absent').forEach(function (r) {
    r.addEventListener('change', function () {
      updateRowHighlight(r);
    });
  });
}

function updateRowHighlight(radio) {
  var row = radio.closest('tr');
  if (!row) return;
  row.classList.remove('att-row-present', 'att-row-absent');
  if (radio.value === 'Present' && radio.checked) {
    row.classList.add('att-row-present');
  } else if (radio.value === 'Absent' && radio.checked) {
    row.classList.add('att-row-absent');
  }
}

// ── Live search for tables ─────────────────────────────
function initTableSearch() {
  var searchInput = document.getElementById('table-search');
  if (!searchInput) return;

  searchInput.addEventListener('input', function () {
    var query = this.value.toLowerCase();
    var rows  = document.querySelectorAll('.searchable-row');
    rows.forEach(function (row) {
      var text = row.textContent.toLowerCase();
      row.style.display = text.includes(query) ? '' : 'none';
    });
  });
}

// ── Percentage bar colour ──────────────────────────────
function initPctBars() {
  document.querySelectorAll('.pct-fill').forEach(function (bar) {
    var pct = parseFloat(bar.getAttribute('data-pct') || '0');
    bar.style.width = Math.min(pct, 100) + '%';
    bar.classList.remove('low', 'medium');
    if (pct < 50) bar.classList.add('low');
    else if (pct < 75) bar.classList.add('medium');
  });
}

// ── Set current date as default for date pickers ──────
function initDateDefaults() {
  var today = new Date().toISOString().split('T')[0];
  document.querySelectorAll('input[type="date"][data-today]').forEach(function (el) {
    if (!el.value) el.value = today;
  });
}

// ── Topbar: live date display ──────────────────────────
function initTopbarDate() {
  var el = document.querySelector('.topbar-date');
  if (!el) return;
  var d = new Date();
  var options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  el.textContent = d.toLocaleDateString('en-IN', options);
}

// ── Attendance row initial highlight ──────────────────
function initRowHighlights() {
  document.querySelectorAll('.att-radio-present:checked').forEach(function (r) {
    var row = r.closest('tr');
    if (row) row.classList.add('att-row-present');
  });
  document.querySelectorAll('.att-radio-absent:checked').forEach(function (r) {
    var row = r.closest('tr');
    if (row) row.classList.add('att-row-absent');
  });
}

// ── Active sidebar link ────────────────────────────────
function initActiveNav() {
  var path = window.location.pathname;
  document.querySelectorAll('.sidebar-nav a').forEach(function (a) {
    if (a.getAttribute('href') && path.startsWith(a.getAttribute('href'))) {
      a.classList.add('active');
    }
  });
}

// ── Boot ───────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  initToasts();
  initSidebar();
  initConfirmDelete();
  initAttendanceBulk();
  initTableSearch();
  initPctBars();
  initDateDefaults();
  initTopbarDate();
  initRowHighlights();
  initActiveNav();
});
