
let selectedLessonId = null;
let selectedChildId = null;
let childrenData = [];
let lessonsData = [];

document.addEventListener('DOMContentLoaded', () => {
    loadPublicSchedule();
});

async function loadPublicSchedule() {
    const container = document.getElementById('lessons-container');

    try {
        // Расписание доступно всем посетителям
        lessonsData = await apiRequest('/lessons');

        if (!lessonsData || lessonsData.length === 0) {
            container.innerHTML =
                '<p style="text-align:center;color:var(--gray);">Пока нет доступных занятий</p>';
            return;
        }

        container.innerHTML = lessonsData.map(lesson => {
            const isFull = lesson.free_places <= 0;

            return `
                <div class="card" style="display:flex;justify-content:space-between;align-items:center;opacity:${isFull ? 0.6 : 1};">
                    <div>
                        <h3 style="margin:0 0 5px 0;">${lesson.title}</h3>
                        <div style="font-size:14px;color:var(--gray);margin-bottom:5px;">
                            📅 ${formatDate(lesson.starts_at)}
                        </div>
                        <div style="font-size:13px;">
                            Свободных мест:
                            <b>${isFull ? 'Нет' : lesson.free_places}</b>
                        </div>
                    </div>

                    <button
                        class="btn ${isFull ? 'btn-gray' : ''}"
                        ${isFull ? 'disabled' : ''}
                        onclick="startBooking(${lesson.id})">
                        ${isFull ? 'Мест нет' : 'Записаться'}
                    </button>
                </div>
            `;
        }).join('');

    } catch (error) {
        container.innerHTML =
            `<p style="color:red;text-align:center;">Ошибка загрузки: ${error.message}</p>`;
    }
}

async function startBooking(lessonId) {
    selectedLessonId = lessonId;

    const lesson = lessonsData.find(item => item.id === lessonId);

    document.getElementById('book-lesson-info').innerText =
        `Занятие: ${lesson ? lesson.title : ''}`;

    const token = localStorage.getItem('family_token');

    if (!token && !USE_MOCK) {
        openModal('modal-public');
        return;
    }

    try {
        childrenData = await familyRequest('/family/children');

        const list = document.getElementById('book-children-list');

        if (!childrenData || childrenData.length === 0) {
            showToast('В семье пока нет детей', 'error');
            return;
        }

        selectedChildId = childrenData[0].id;

        list.innerHTML = childrenData.map(child => {
            const childName = [
                child.first_name,
                child.last_name
            ].filter(Boolean).join(' ');

            return `
                <button
                    class="btn btn-gray btn-block"
                    onclick="selectChildForBook(${child.id})">
                    ${childName || 'Имя не указано'}
                </button>
            `;
        }).join('');

        selectChildForBook(selectedChildId);
        openModal('modal-book');

    } catch (error) {
        showToast(error.message, 'error');
    }
}

function selectChildForBook(id) {
    selectedChildId = id;

    const buttons = document.querySelectorAll('#book-children-list button');

    buttons.forEach((button, index) => {
        if (childrenData[index].id === id) {
            button.classList.remove('btn-gray');
        } else {
            button.classList.add('btn-gray');
        }
    });
}

async function confirmBooking() {
    if (!selectedChildId) {
        showToast('Выберите ребёнка', 'error');
        return;
    }

    try {
        await familyRequest('/family/bookings', {
            method: 'POST',
            body: JSON.stringify({
                child_id: selectedChildId,
                lesson_id: selectedLessonId
            })
        });

        closeModal('modal-book');
        showToast('Ребёнок успешно записан!');
        await loadPublicSchedule();

    } catch (error) {
        showToast(error.message, 'error');
    }
}
