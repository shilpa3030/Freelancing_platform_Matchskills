(function () {
    'use strict';

    window.DashboardCommon = {
        apiUrl: function () {
            return window.__API_BASE__ || (window.location.origin + '/api');
        },

        getToken: function () {
            return localStorage.getItem('authToken');
        },

        formatCurrency: function (amount) {
            if (amount == null || isNaN(amount)) return '—';
            return '₹' + Number(amount).toLocaleString('en-IN');
        },

        formatDate: function (iso) {
            if (!iso) return '—';
            var d = new Date(iso);
            return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
        },

        statusBadgeClass: function (status) {
            var s = (status || '').replace(/_/g, '-');
            return 'badge-status status-' + s;
        },

        authFetch: async function (path, options) {
            var token = DashboardCommon.getToken();
            if (!token) {
                window.location.href = '/?login=1';
                return null;
            }
            var opts = options || {};
            var headers = Object.assign({}, opts.headers || {}, {
                'Authorization': 'Bearer ' + token
            });
            if (opts.body instanceof FormData) {
                delete headers['Content-Type'];
            } else if (opts.body && typeof opts.body === 'string' && !headers['Content-Type']) {
                headers['Content-Type'] = 'application/json';
            }
            var res = await fetch(DashboardCommon.apiUrl() + path, Object.assign({}, opts, { headers: headers }));
            return res;
        },

        requireRole: async function (role) {
            var token = DashboardCommon.getToken();
            if (!token) {
                window.location.href = '/?login=1';
                return null;
            }
            var res = await fetch(DashboardCommon.apiUrl() + '/auth/me', {
                headers: { 'Authorization': 'Bearer ' + token }
            });
            var data = await res.json();
            if (!data || !data.role) {
                localStorage.removeItem('authToken');
                window.location.href = '/?login=1';
                return null;
            }
            if (data.role !== role) {
                window.location.href = '/';
                return null;
            }
            return data;
        },

        toast: function (message, type) {
            var cls = type === 'success' ? 'alert-success' : 'alert-danger';
            var el = document.createElement('div');
            el.className = 'alert ' + cls + ' alert-dismissible fade show dash-toast';
            el.setAttribute('role', 'alert');
            el.innerHTML = message + '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
            document.body.appendChild(el);
            setTimeout(function () { el.remove(); }, 5000);
        },

        initShell: function () {
            var sidebar = document.getElementById('dashSidebar');
            var toggle = document.getElementById('dashMobileToggle');
            var backdrop = document.getElementById('dashBackdrop');
            function close() {
                if (sidebar) sidebar.classList.remove('is-open');
                if (backdrop) backdrop.classList.remove('show');
            }
            function open() {
                if (sidebar) sidebar.classList.add('is-open');
                if (backdrop) backdrop.classList.add('show');
            }
            if (toggle && sidebar) {
                toggle.addEventListener('click', function () {
                    if (sidebar.classList.contains('is-open')) close();
                    else open();
                });
            }
            if (backdrop) backdrop.addEventListener('click', close);
            document.querySelectorAll('#clientLogout, #freelancerLogout').forEach(function (btn) {
                btn.addEventListener('click', function (e) {
                    e.preventDefault();
                    localStorage.removeItem('authToken');
                    window.location.href = '/';
                });
            });
        }
    };

    document.addEventListener('DOMContentLoaded', function () {
        if (document.body.classList.contains('dashboard-body')) {
            DashboardCommon.initShell();
        }
    });
})();
