const API_URL = window.location.origin + '/api';
let currentUser = null;
let authToken = null;
let socket = null;
let LANDING_HTML_CACHE = null;

function cacheLandingHtml() {
    var mc = document.getElementById('main-content');
    if (mc && LANDING_HTML_CACHE === null) {
        LANDING_HTML_CACHE = mc.innerHTML;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    cacheLandingHtml();

    checkAuth()
        .then(function () {
            document.body.classList.remove('auth-checking');

            if (currentUser && window.location.pathname === '/') {
                if (currentUser.role === 'client') {
                    window.location.href = '/dashboard/client';
                    return;
                }
                if (currentUser.role === 'student') {
                    window.location.href = '/dashboard/freelancer';
                    return;
                }
                if (currentUser.role === 'admin') {
                    initializeSocket();
                    loadDashboard();
                    return;
                }
            }

            var params = new URLSearchParams(window.location.search);
            if (params.get('login') === '1') {
                showLogin();
            } else if (params.get('register') === '1') {
                showRegister();
            }
        })
        .catch(function () {
            document.body.classList.remove('auth-checking');
        });
});

function checkAuth() {
    authToken = localStorage.getItem('authToken');
    if (!authToken) {
        currentUser = null;
        updateNavigation(false);
        return Promise.resolve(null);
    }
    return fetch(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${authToken}` }
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            if (data.id) {
                currentUser = data;
                updateNavigation(true);
                if (currentUser.role === 'admin') {
                    initializeSocket();
                }
                return currentUser;
            }
            localStorage.removeItem('authToken');
            authToken = null;
            currentUser = null;
            updateNavigation(false);
            return null;
        })
        .catch(function (err) {
            console.error('Auth error:', err);
            localStorage.removeItem('authToken');
            authToken = null;
            currentUser = null;
            updateNavigation(false);
            return null;
        });
}

function updateNavigation(isAuthenticated) {
    var guestSignin = document.getElementById('nav-guest-signin');
    var guestCta = document.getElementById('nav-guest-cta');
    var navAdmin = document.getElementById('nav-admin-console');
    var navLogout = document.getElementById('nav-logout');

    if (!guestSignin || !guestCta) return;

    if (isAuthenticated && currentUser && currentUser.role === 'admin') {
        guestSignin.classList.add('d-none');
        guestCta.classList.add('d-none');
        if (navAdmin) navAdmin.classList.remove('d-none');
        if (navLogout) navLogout.classList.remove('d-none');
        return;
    }

    if (navAdmin) navAdmin.classList.add('d-none');
    if (navLogout) navLogout.classList.add('d-none');
    guestSignin.classList.remove('d-none');
    guestCta.classList.remove('d-none');
}

function showHome() {
    if (LANDING_HTML_CACHE) {
        document.getElementById('main-content').innerHTML = LANDING_HTML_CACHE;
    } else {
        window.location.href = '/';
    }
}

function showLogin() {
    document.getElementById('main-content').innerHTML = `
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-md-5">
                    <div class="card card-custom p-4 p-md-5 fade-in">
                        <div class="text-center mb-4">
                            <div class="hero-gradient-bar mx-auto mb-3"></div>
                            <h2 class="font-heading h4 mb-1">Welcome back</h2>
                            <p class="text-secondary small mb-0">Sign in to open your dashboard</p>
                        </div>
                        <form id="loginForm">
                            <div class="mb-3">
                                <label class="form-label small fw-semibold">Email</label>
                                <input type="email" class="form-control form-control-lg" id="loginEmail" required autocomplete="email">
                            </div>
                            <div class="mb-4">
                                <label class="form-label small fw-semibold">Password</label>
                                <input type="password" class="form-control form-control-lg" id="loginPassword" required autocomplete="current-password">
                            </div>
                            <button type="submit" class="btn btn-primary-custom w-100 py-3 mb-3">
                                <i class="fas fa-sign-in-alt me-2"></i>Sign in
                            </button>
                        </form>
                        <p class="text-center small text-secondary mb-2">New here? <a href="#" class="fw-semibold text-decoration-none" style="color:var(--fh-orange)" onclick="showRegister(); return false;">Create an account</a></p>
                        <p class="text-center small mb-0"><a href="#" class="text-muted text-decoration-none" onclick="showHome(); return false;">← Back to home</a></p>
                    </div>
                </div>
            </div>
        </div>`;
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
}

function handleLogin(e) {
    e.preventDefault();
    var email = document.getElementById('loginEmail').value;
    var password = document.getElementById('loginPassword').value;

    fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            if (data.access_token) {
                localStorage.setItem('authToken', data.access_token);
                authToken = data.access_token;
                currentUser = data.user;
                updateNavigation(true);
                showNotification('Signed in successfully.', 'success');
                if (data.user.role === 'client') {
                    window.location.href = '/dashboard/client';
                    return;
                }
                if (data.user.role === 'student') {
                    window.location.href = '/dashboard/freelancer';
                    return;
                }
                initializeSocket();
                loadDashboard();
            } else {
                showNotification('Sign in failed: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(function (error) {
            showNotification('Error: ' + error.message, 'error');
        });
}

function showRegister() {
    document.getElementById('main-content').innerHTML = `
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-md-6 col-lg-5">
                    <div class="card card-custom p-4 p-md-5 fade-in">
                        <div class="text-center mb-4">
                            <div class="hero-gradient-bar mx-auto mb-3"></div>
                            <h2 class="font-heading h4 mb-1">Create your account</h2>
                            <p class="text-secondary small mb-0">Clients and freelancers use the same signup—pick your role below.</p>
                        </div>
                        <form id="registerForm">
                            <div class="mb-3">
                                <label class="form-label small fw-semibold">I am a</label>
                                <select class="form-select form-select-lg" id="userRole" required>
                                    <option value="">Choose…</option>
                                    <option value="student">Freelancer / developer / designer</option>
                                    <option value="client">Client / team hiring talent</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label small fw-semibold">Email</label>
                                <input type="email" class="form-control form-control-lg" id="regEmail" required autocomplete="email">
                            </div>
                            <div class="mb-3">
                                <label class="form-label small fw-semibold">Password</label>
                                <input type="password" class="form-control form-control-lg" id="regPassword" required minlength="6" autocomplete="new-password">
                                <small class="text-secondary">At least 6 characters</small>
                            </div>
                            <div id="studentFields" style="display:none;">
                                <div class="mb-3">
                                    <label class="form-label small fw-semibold">Full name</label>
                                    <input type="text" class="form-control" id="studentName">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-semibold">College / org</label>
                                    <input type="text" class="form-control" id="studentCollege">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-semibold">Year / level</label>
                                    <select class="form-select" id="studentYear">
                                        <option>1st Year</option>
                                        <option>2nd Year</option>
                                        <option>3rd Year</option>
                                        <option>4th Year</option>
                                        <option>Graduate</option>
                                    </select>
                                </div>
                            </div>
                            <div id="clientFields" style="display:none;">
                                <div class="mb-3">
                                    <label class="form-label small fw-semibold">Company name</label>
                                    <input type="text" class="form-control" id="clientCompany">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-semibold">Short description</label>
                                    <textarea class="form-control" id="clientDesc" rows="2"></textarea>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-cta-orange w-100 py-3 mb-3">
                                <i class="fas fa-rocket me-2"></i>Create account
                            </button>
                        </form>
                        <p class="text-center small text-secondary mb-2">Already registered? <a href="#" class="fw-semibold text-decoration-none" style="color:var(--fh-primary)" onclick="showLogin(); return false;">Sign in</a></p>
                        <p class="text-center small mb-0"><a href="#" class="text-muted text-decoration-none" onclick="showHome(); return false;">← Back to home</a></p>
                    </div>
                </div>
            </div>
        </div>`;

    document.getElementById('userRole').addEventListener('change', toggleRoleFields);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
}

function toggleRoleFields() {
    var role = document.getElementById('userRole').value;
    document.getElementById('studentFields').style.display = role === 'student' ? 'block' : 'none';
    document.getElementById('clientFields').style.display = role === 'client' ? 'block' : 'none';
}

function handleRegister(e) {
    e.preventDefault();
    var role = document.getElementById('userRole').value;
    var email = document.getElementById('regEmail').value;
    var password = document.getElementById('regPassword').value;
    var payload = { email, password, role };

    if (role === 'student') {
        payload.name = document.getElementById('studentName').value;
        payload.college = document.getElementById('studentCollege').value;
        payload.year = document.getElementById('studentYear').value;
    } else if (role === 'client') {
        payload.company = document.getElementById('clientCompany').value;
        payload.description = document.getElementById('clientDesc').value;
    }

    fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
        .then(function (r) {
            return r.json();
        })
        .then(function (data) {
            if (data.user_id) {
                showNotification('Account created. Please sign in.', 'success');
                showLogin();
            } else {
                showNotification('Registration failed: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(function (error) {
            showNotification('Error: ' + error.message, 'error');
        });
}

function loadDashboard() {
    if (!currentUser) {
        showLogin();
        return;
    }
    if (currentUser.role === 'student') {
        window.location.href = '/dashboard/freelancer';
        return;
    }
    if (currentUser.role === 'client') {
        window.location.href = '/dashboard/client';
        return;
    }
    if (currentUser.role === 'admin') {
        loadAdminDashboard();
    }
}

function initializeSocket() {
    if (socket) return;
    socket = io(window.location.origin);
    socket.on('connect', function () {
        console.log('Socket connected');
    });
    socket.on('receive_message', function (data) {
        console.log('Message:', data);
    });
}

function showNotification(message, type) {
    var alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    var iconClass = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    var el = document.createElement('div');
    el.className = 'alert ' + alertClass + ' alert-dismissible fade show position-fixed shadow';
    el.style.cssText = 'top:88px;right:16px;z-index:9999;min-width:280px;border-radius:12px;';
    el.innerHTML =
        '<i class="fas ' + iconClass + ' me-2"></i>' +
        message +
        '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
    document.body.appendChild(el);
    setTimeout(function () {
        el.remove();
    }, 5000);
}

function logout() {
    localStorage.removeItem('authToken');
    authToken = null;
    currentUser = null;
    updateNavigation(false);
    if (socket) {
        socket.disconnect();
        socket = null;
    }
    showHome();
    showNotification('Signed out.', 'success');
}

function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatCurrency(amount) {
    return '₹' + amount.toLocaleString('en-IN');
}
