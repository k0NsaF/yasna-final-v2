let currentChildId = null;
let childrenData = [];

document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    if (token) {
        localStorage.setItem('family_token', token);
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    // Если токена нет, просто покажем ошибку, но не закроем страницу
    if (!localStorage.getItem('family_token')) {
        document.getElementById('family-title').innerText = "Ошибка: Нет токена";
        document.getElementById('upcoming-lessons').innerHTML = '<p style="color:red;">Ссылка недействительна.</p>';
        return;
    }

    await loadFamilyData();
});

async function loadFamilyData() {
    try {
        const [family, children, balance] = await Promise.all([
            familyRequest('/family/me'),
            familyRequest('/family/children'),
            familyRequest('/family/subscriptions/balance')
        ]);

        document.getElementById('family-title').innerText = family.name || 'Личный кабинет';
        childrenData = Array.isArray(children) ? children : [];
        renderChildrenTabs();

        document.getElementById('balance-lessons').innerText = balance.remaining_lessons ?? 0;
        document.getElementById('balance-money').innerText = formatMoney(balance.money_balance ?? 0);

        await loadUpcomingLessons();
        await loadHistory();
    } catch (err) {
        document.getElementById('family-title').innerText = "Ошибка доступа";
        document.getElementById('upcoming-lessons').innerHTML = `<p style="color: red;">Не удалось загрузить данные: ${err.message}</p>`;
    }
}

function getChildName(child) {
    return [child.first_name, child.last_name].filter(Boolean).join(' ') || 'Ребёнок';
}

function renderChildrenTabs() {
    const container = document.getElementById('children-tabs');
    if (!container) return;

    if (childrenData.length === 0) {
        currentChildId = null;
        container.innerHTML = '<p style="color: var(--gray);">Дети пока не добавлены</p>';
        return;
    }

    if (!childrenData.some(child => Number(child.id) === Number(currentChildId))) {
        currentChildId = childrenData[0].id;
    }

    container.innerHTML = childrenData.map(child => {
        const isActive = Number(child.id) === Number(currentChildId);
        return `
            <button type="button" class="btn ${isActive ? '' : 'btn-gray'}" style="padding: 8px 16px; font-size: 14px;" onclick="selectChild(${Number(child.id)})">
                ${getChildName(child)}
            </button>
        `;
    }).join('');
}

async function selectChild(id) {
    currentChildId = Number(id);
    renderChildrenTabs();
    await loadUpcomingLessons();
}

async function loadUpcomingLessons() {
    const container = document.getElementById('upcoming-lessons');
    if (!container) return;

    if (!currentChildId) {
        container.innerHTML = `<p style="color: var(--gray);">Сначала добавьте ребёнка в семью</p>`;
        return;
    }

    container.innerHTML = `<p style="color: var(--gray);">Загружаем записи...</p>`;

    try {
        const [bookings, lessons] = await Promise.all([
            familyRequest('/family/bookings'),
            familyRequest('/lessons')
        ]);

        const safeBookings = Array.isArray(bookings) ? bookings : [];
        const safeLessons = Array.isArray(lessons) ? lessons : [];
        const lessonsMap = new Map(safeLessons.map(l => [Number(l.id), l]));

        const childBookings = safeBookings
            .filter(b => Number(b.child_id) === Number(currentChildId))
            .sort((a, b) => {
                const dateA = lessonsMap.get(Number(a.lesson_id)) ? new Date(lessonsMap.get(Number(a.lesson_id)).starts_at).getTime() : 0;
                const dateB = lessonsMap.get(Number(b.lesson_id)) ? new Date(lessonsMap.get(Number(b.lesson_id)).starts_at).getTime() : 0;
                return dateA - dateB;
            });

        if (childBookings.length === 0) {
            container.innerHTML = `<p style="color: var(--gray);">У ребёнка пока нет записей</p>`;
            return;
        }

        container.innerHTML = childBookings.map(booking => {
            const lesson = lessonsMap.get(Number(booking.lesson_id));
            const title = lesson ? lesson.title : `Занятие №${booking.lesson_id}`;
            const date = lesson ? formatDate(lesson.starts_at) : 'Информация недоступна';
            const canCancel = booking.status === 'booked' && lesson && new Date(lesson.starts_at).getTime() > Date.now();
            const statusText = booking.status === 'cancelled' ? 'Отменена' : 'Записан';
            const statusColor = booking.status === 'cancelled' ? '#DC2626' : '#16A34A';

            return `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: #F9FAFB; border-radius: 10px; gap: 12px; flex-wrap: wrap;">
                    <div>
                        <div style="font-weight: bold;">${title}</div>
                        <div style="font-size: 13px; color: var(--gray); margin-top: 4px;">${date}</div>
                        <div style="font-size: 13px; color: ${statusColor}; margin-top: 4px;">Статус: ${statusText}</div>
                    </div>
                    ${canCancel ? `<button type="button" class="btn btn-gray" onclick="cancelBooking(${Number(booking.id)})">Отменить</button>` : ''}
                </div>
            `;
        }).join('');
    } catch (err) {
        container.innerHTML = `<p style="color: red;">Не удалось загрузить записи: ${err.message}</p>`;
    }
}

async function cancelBooking(bookingId) {
    if (!confirm('Вы действительно хотите отменить запись?')) return;
    try {
        await familyRequest(`/family/bookings/${bookingId}`, { method: 'DELETE' });
        showToast('Запись отменена');
        await loadUpcomingLessons();
    } catch (err) { showToast('Ошибка: ' + err.message, 'error'); }
}

async function loadHistory() {
    const container = document.getElementById('history-list');
    if (!container) return;
    container.innerHTML = '<p style="color: var(--gray);">История загружается...</p>';
}