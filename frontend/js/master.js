document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    switchTab('dashboard');
});

function switchTab(tabId) {
    document.querySelectorAll('section[id^="tab-"]').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.nav-btn').forEach(el => {
        el.style.color = 'var(--gray)';
        el.style.borderBottom = 'none';
    });

    const section = document.getElementById(`tab-${tabId}`);
    const activeBtn = document.querySelector(`.nav-btn[data-tab="${tabId}"]`);
    
    if (section) section.style.display = 'block';
    if (activeBtn) {
        activeBtn.style.color = 'var(--dark)';
        activeBtn.style.borderBottom = '3px solid var(--yellow)';
    }

    if (tabId === 'dashboard') loadDashboard();
    if (tabId === 'schedule') loadSchedule();
    if (tabId === 'attendance') loadAttendance();
    if (tabId === 'families') loadFamilies();
    if (tabId === 'finance') loadFinance();
}

// --- ГЛАВНАЯ ПАНЕЛЬ ---
async function loadDashboard() {
    try {
        const [lessons, families, subscriptions] = await Promise.all([
            masterRequest('/master/lessons'),
            masterRequest('/master/families'),
            masterRequest('/master/subscriptions')
        ]);

        const today = new Date();
        const todayLessons = lessons.filter(lesson => {
            const date = new Date(lesson.starts_at);
            return date.getFullYear() === today.getFullYear() && date.getMonth() === today.getMonth() && date.getDate() === today.getDate();
        });

        const childrenTotal = families.reduce((sum, family) => sum + (family.children?.length || 0), 0);

        const endingSubs = subscriptions.filter(sub => {
            if (!sub.is_active) return false;
            const remaining = sub.total_lessons - sub.used_lessons;
            const expiresSoon = sub.expires_at && new Date(sub.expires_at) <= new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
            return remaining <= 2 || expiresSoon;
        });

        document.getElementById('stat-lessons').innerText = todayLessons.length;
        document.getElementById('stat-children').innerText = childrenTotal;
        document.getElementById('stat-ending').innerText = endingSubs.length;
    } catch (e) { showToast('Ошибка загрузки главной: ' + e.message, 'error'); }
}

// --- РАСПИСАНИЕ ---
async function loadSchedule() {
    try {
        const lessons = await masterRequest('/master/lessons');
        const tbody = document.getElementById('schedule-list');
        if (!lessons || lessons.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;">Нет занятий</td></tr>`;
            return;
        }
        tbody.innerHTML = lessons.map(l => `
            <tr>
                <td>${formatDate(l.starts_at)}</td>
                <td>${l.title}</td>
                <td>${l.booked_count} / ${l.capacity}</td>
                <td>${l.is_active ? 'Активно' : 'Отменено'}</td>
            </tr>
        `).join('');
    } catch (e) { showToast(e.message, 'error'); }
}

async function createLesson() {
    const data = {
        title: document.getElementById('lesson-title').value,
        starts_at: document.getElementById('lesson-date').value,
        duration_minutes: 60,
        capacity: parseInt(document.getElementById('lesson-capacity').value),
        price: 0
    };
    try {
        await masterRequest('/master/lessons', { method: 'POST', body: JSON.stringify(data) });
        closeModal('modal-create-lesson');
        showToast('Занятие создано');
        loadSchedule();
        loadDashboard();
    } catch (e) { showToast(e.message, 'error'); }
}

// --- ПОСЕЩАЕМОСТЬ ---
async function loadAttendance() {
    try {
        const list = await masterRequest('/master/attendance');
        const tbody = document.getElementById('attendance-list');
        if (!list || list.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;">Нет записей</td></tr>`;
            return;
        }
        tbody.innerHTML = list.map(item => {
            let statusText = 'Не отмечено';
            let statusClass = 'badge-gray';
            if (item.status === 'attended') { statusText = 'Посетил'; statusClass = 'badge-green'; }
            if (item.status === 'missed') { statusText = 'Пропустил'; statusClass = 'badge-red'; }

            return `
                <tr>
                    <td>${item.childName}</td>
                    <td>${item.lessonTitle}</td>
                    <td><span class="badge ${statusClass}">${statusText}</span></td>
                    <td>
                        <button type="button" class="btn" onclick="markAttendance(${item.id}, 'attended')">Посетил</button>
                        <button type="button" class="btn btn-gray" onclick="markAttendance(${item.id}, 'missed')">Пропустил</button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (e) { showToast(e.message, 'error'); }
}

async function markAttendance(id, status) {
    try {
        await masterRequest(`/master/bookings/${id}/attendance`, { method: 'PUT', body: JSON.stringify({ status }) });
        showToast('Отметка сохранена');
        loadAttendance();
    } catch (e) { showToast(e.message, 'error'); }
}

// --- СЕМЬИ ---
async function loadFamilies() {
    try {
        const families = await masterRequest('/master/families');
        const tbody = document.getElementById('families-list');
        if (!families || families.length === 0) {
            tbody.innerHTML = `<tr><td colspan="3" style="text-align:center;">Нет семей</td></tr>`;
            return;
        }
        tbody.innerHTML = families.map(f => `
            <tr>
                <td>${f.name}</td>
                <td>${f.children?.length ? f.children.join(', ') : 'Нет детей'}</td>
                <td><button type="button" class="btn" onclick="generateLink(${f.id})">Выдать ссылку</button></td>
            </tr>
        `).join('');
    } catch (e) { showToast(e.message, 'error'); }
}

async function createFamily() {
    const familyData = {
        name: document.getElementById('family-name').value,
        phone: document.getElementById('family-phone').value
    };
    const childData = {
        first_name: document.getElementById('child-name').value,
        last_name: document.getElementById('child-lastname').value,
        birth_date: document.getElementById('child-birthdate').value
    };
    try {
        const family = await masterRequest('/master/families', { method: 'POST', body: JSON.stringify(familyData) });
        await masterRequest(`/master/families/${family.id}/children`, { method: 'POST', body: JSON.stringify(childData) });
        closeModal('modal-create-family');
        showToast('Семья создана');
        loadFamilies();
        loadDashboard();
    } catch (e) { showToast(e.message, 'error'); }
}

async function generateLink(familyId) {
    try {
        const res = await masterRequest(`/master/families/${familyId}/link`, { method: 'POST' });
        // Формируем ссылку, убирая возможные ошибки с путями
        let path = window.location.pathname.replace('master.html', 'family.html');
        let url = window.location.origin + path + "?token=" + res.access_token;
        
        document.getElementById('family-link-input').value = url;
        openModal('modal-show-link');
    } catch (e) { showToast(e.message, 'error'); }
}

function copyLinkAndClose() {
    const input = document.getElementById('family-link-input');
    input.select();
    document.execCommand('copy');
    closeModal('modal-show-link');
    showToast('Ссылка скопирована');
}

// --- ФИНАНСЫ ---
async function loadFinance() {
    try {
        const [payments, subscriptions, families] = await Promise.all([
            masterRequest('/master/payments'),
            masterRequest('/master/subscriptions'),
            masterRequest('/master/families')
        ]);

        // Заполняем платежи
        const tbodyP = document.getElementById('finance-list');
        if (payments && payments.length > 0) {
            tbodyP.innerHTML = payments.map(p => `
                <tr>
                    <td>Семья №${p.family_id}</td>
                    <td>${formatMoney(p.amount)}</td>
                    <td>${p.status}</td>
                    <td>${formatDate(p.created_at)}</td>
                </tr>
            `).join('');
        } else { tbodyP.innerHTML = `<tr><td colspan="4" style="text-align:center;">Нет платежей</td></tr>`; }

        // Заполняем абонементы
        const tbodyS = document.getElementById('subscriptions-list');
        const familyNames = {};
        families.forEach(f => familyNames[f.id] = f.name);

        if (subscriptions && subscriptions.length > 0) {
            tbodyS.innerHTML = subscriptions.map(s => `
                <tr>
                    <td>${s.id}</td>
                    <td>${familyNames[s.family_id] || 'Семья №'+s.family_id}</td>
                    <td>${s.title}</td>
                    <td>${s.total_lessons - s.used_lessons} из ${s.total_lessons}</td>
                    <td>${formatMoney(s.price)}</td>
                </tr>
            `).join('');
        } else { tbodyS.innerHTML = `<tr><td colspan="5" style="text-align:center;">Нет абонементов</td></tr>`; }

        // Заполняем select для создания абонемента
        const select = document.getElementById('subscription-family');
        if (select) {
            select.innerHTML = '<option value="">Выберите семью</option>';
            families.forEach(f => { select.innerHTML += `<option value="${f.id}">${f.name}</option>`; });
        }
    } catch (e) { showToast('Ошибка загрузки финансов: ' + e.message, 'error'); }
}

async function createSubscription() {
    const data = {
        family_id: parseInt(document.getElementById('subscription-family').value),
        title: document.getElementById('subscription-title').value,
        total_lessons: parseInt(document.getElementById('subscription-total').value),
        price: parseFloat(document.getElementById('subscription-price').value),
        expires_at: document.getElementById('subscription-expires').value || null
    };
    try {
        await masterRequest('/master/subscriptions', { method: 'POST', body: JSON.stringify(data) });
        closeModal('modal-create-subscription');
        showToast('Абонемент создан');
        loadFinance();
    } catch (e) { showToast(e.message, 'error'); }
}