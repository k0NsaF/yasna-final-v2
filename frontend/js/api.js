
const API_URL = "http://localhost:8000/api";

// ==========================================
// ОСНОВНОЙ ЗАПРОС К API
// ==========================================

async function apiRequest(path, options = {}) {
    const headers = { ...options.headers };

    // Для обычных JSON-запросов указываем тип данных.
    // Для FormData браузер сам установит нужный Content-Type.
    if (!(options.body instanceof FormData)) {
        headers["Content-Type"] =
            headers["Content-Type"] || "application/json";
    }

    const response = await fetch(API_URL + path, {
        ...options,
        headers
    });

    let data = null;

    const contentType = response.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {
        data = await response.json();
    } else {
        data = await response.text();
    }

    if (!response.ok) {
        const message =
            typeof data === "object" && data !== null
                ? data.detail || "Ошибка запроса"
                : data || "Ошибка запроса";

        throw new Error(
            Array.isArray(message)
                ? message.map(item => item.msg).join(", ")
                : message
        );
    }

    return data;
}


// ==========================================
// ЗАПРОСЫ МАСТЕРА
// ==========================================

async function masterRequest(path, options = {}) {
    const token = localStorage.getItem("master_token");

    if (!token) {
        throw new Error("Нет авторизации мастера. Войдите заново.");
    }

    return apiRequest(path, {
        ...options,
        headers: {
            ...options.headers,
            "Authorization": `Bearer ${token}`
        }
    });
}


// ==========================================
// ЗАПРОСЫ СЕМЬИ
// ==========================================

async function familyRequest(path, options = {}) {
    const urlParams = new URLSearchParams(window.location.search);

    const token =
        urlParams.get("token") ||
        localStorage.getItem("family_token");

    if (!token) {
        throw new Error("Нет персональной ссылки семьи.");
    }

    return apiRequest(path, {
        ...options,
        headers: {
            ...options.headers,
            "Authorization": `Bearer ${token}`
        }
    });
}


// ==========================================
// ЗАГРУЗКА ЧЕКА
// ==========================================

// paymentId — номер платежа.
// formData — файл чека, выбранный мастером.

async function uploadReceipt(paymentId, formData) {
    const token = localStorage.getItem("master_token");

    if (!token) {
        throw new Error("Нет авторизации мастера.");
    }

    const response = await fetch(
        `${API_URL}/master/payments/${paymentId}/receipt/file`,
        {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            },
            body: formData
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Ошибка загрузки чека");
    }

    return data;
}
