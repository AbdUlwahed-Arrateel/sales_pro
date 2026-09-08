// ═══ Sidebar Toggle ═══
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('sidebarOverlay').classList.toggle('show');
}

// ═══ Dropdown Groups ═══
function toggleGroup(btn) {
    const items = btn.nextElementSibling;
    const isOpen = items.classList.contains('show');
    // Close all other groups
    document.querySelectorAll('.sb-group-items.show').forEach(el => {
        el.classList.remove('show');
        el.previousElementSibling.classList.remove('open');
    });
    // Toggle clicked
    if (!isOpen) {
        items.classList.add('show');
        btn.classList.add('open');
    }
}

// ═══ Clock ═══
function updateClock() {
    const el = document.getElementById('topbarClock');
    if (!el) return;
    const now = new Date();
    const d = now.toLocaleDateString('ar-LY', {weekday:'short', month:'short', day:'numeric'});
    const t = now.toLocaleTimeString('ar-LY', {hour:'2-digit', minute:'2-digit'});
    el.textContent = `${d} — ${t}`;
}
updateClock();
setInterval(updateClock, 1000);

// ═══ Auto-hide alerts ═══
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(el => {
        el.style.transition = 'opacity .5s';
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 500);
    });
}, 4500);

// ═══ CSRF ═══
function getCsrfToken() {
    return document.cookie.split('; ').find(r => r.startsWith('csrftoken='))?.split('=')[1] || '';
}

// ═══ Modal helpers ═══
function openModal(id) {
    const el = document.getElementById(id);
    if (el) { el.classList.add('show'); document.body.style.overflow = 'hidden'; }
}
function closeModal(id) {
    const el = document.getElementById(id);
    if (el) { el.classList.remove('show'); document.body.style.overflow = ''; }
}
document.querySelectorAll('.modal-backdrop').forEach(m => {
    m.addEventListener('click', function(e) { if (e.target === this) closeModal(this.id); });
});

// ═══ Confirm delete ═══
document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', function(e) {
        if (!confirm(this.dataset.confirm || 'هل أنت متأكد من الحذف؟')) e.preventDefault();
    });
});

// ═══ Number format ═══
function fmt(n, d=3) { return parseFloat(n).toFixed(d); }
