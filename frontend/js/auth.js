function checkAuth() {
    const token = localStorage.getItem("master_token");
    if (!token && !window.location.pathname.includes('login')) {
        window.location.href = "master-login.html";
    }
}

function logout() {
    localStorage.removeItem("master_token");
    window.location.href = "master-login.html";
}