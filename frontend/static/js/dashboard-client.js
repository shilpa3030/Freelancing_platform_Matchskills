(function () {
    'use strict';

    var DC = window.DashboardCommon;

    function rowHighlight(id) {
        var params = new URLSearchParams(window.location.search);
        var focus = params.get('focus');
        if (focus && String(id) === String(focus)) return 'table-row-highlight';
        return '';
    }

    async function loadProjects() {
        var res = await DC.authFetch('/client/projects');
        if (!res || !res.ok) return [];
        return res.json();
    }

    window.ClientDash = {
        overview: async function () {
            await DC.requireRole('client');
            var projects = await loadProjects();
            var total = projects.length;
            var active = projects.filter(function (p) {
                return p.status === 'open' || p.status === 'in_progress';
            }).length;
            var done = projects.filter(function (p) { return p.status === 'completed'; }).length;

            document.getElementById('stat-total').textContent = total;
            document.getElementById('stat-active').textContent = active;
            document.getElementById('stat-completed').textContent = done;

            var recent = projects.slice(0, 5);
            var tbody = document.querySelector('#tbl-recent tbody');
            if (!tbody) return;
            tbody.innerHTML = recent.map(function (p) {
                return '<tr class="' + rowHighlight(p.id) + '">' +
                    '<td><strong>' + escapeHtml(p.title) + '</strong></td>' +
                    '<td><span class="badge ' + DC.statusBadgeClass(p.status) + '">' + escapeHtml(p.status) + '</span></td>' +
                    '<td>' + p.bids_count + '</td>' +
                    '<td><a class="btn btn-sm btn-outline-fh" href="/dashboard/client/projects/' + p.id + '/bids">Bids</a></td>' +
                    '</tr>';
            }).join('') || '<tr><td colspan="4" class="text-muted">No projects yet.</td></tr>';
        },

        myProjects: async function () {
            await DC.requireRole('client');
            var projects = await loadProjects();
            var wrap = document.getElementById('hub-cards');
            var tbody = document.querySelector('#tbl-hub tbody');
            if (wrap) {
                wrap.innerHTML = projects.map(function (p) {
                    return '<div class="col-md-6 col-xl-4 d-flex">' +
                        '<div class="card dash-card fh-hub-card flex-fill">' +
                        '<div class="card-body">' +
                        '<div class="d-flex justify-content-between align-items-start mb-2">' +
                        '<h3 class="h6 mb-0">' + escapeHtml(p.title) + '</h3>' +
                        '<span class="badge ' + DC.statusBadgeClass(p.status) + '">' + escapeHtml(p.status) + '</span></div>' +
                        '<p class="small text-muted mb-3">' + escapeHtml((p.description || '').slice(0, 120)) + (p.description && p.description.length > 120 ? '…' : '') + '</p>' +
                        '<div class="d-flex flex-wrap gap-2">' +
                        '<a href="/dashboard/client/projects/' + p.id + '/bids" class="btn btn-sm btn-fh">View bids</a>' +
                        (p.status === 'in_progress' ? '<button type="button" class="btn btn-sm btn-success btn-complete" data-pid="' + p.id + '">Mark complete</button>' : '') +
                        '</div></div></div></div>';
                }).join('') || '<p class="text-muted">Post your first project to see it here.</p>';

                wrap.querySelectorAll('.btn-complete').forEach(function (btn) {
                    btn.addEventListener('click', function () {
                        completeProject(btn.getAttribute('data-pid'));
                    });
                });
            }
            if (tbody) {
                tbody.innerHTML = projects.map(function (p) {
                    return '<tr class="' + rowHighlight(p.id) + '">' +
                        '<td>' + escapeHtml(p.title) + '</td>' +
                        '<td><span class="badge ' + DC.statusBadgeClass(p.status) + '">' + escapeHtml(p.status) + '</span></td>' +
                        '<td>' + DC.formatCurrency(p.budget_min) + ' – ' + DC.formatCurrency(p.budget_max) + '</td>' +
                        '<td>' + p.bids_count + '</td>' +
                        '<td>' + DC.formatDate(p.created_at) + '</td>' +
                        '<td><a href="/dashboard/client/projects/' + p.id + '/bids" class="btn btn-sm btn-outline-fh">Bids</a></td>' +
                        '</tr>';
                }).join('') || '<tr><td colspan="6" class="text-muted">No data.</td></tr>';
            }
        },

        tableTotal: async function () {
            await DC.requireRole('client');
            var projects = await loadProjects();
            var tbody = document.querySelector('#tbl-total tbody');
            if (!tbody) return;
            tbody.innerHTML = projects.map(function (p) {
                var linkActive = '/dashboard/client/projects/active?focus=' + p.id;
                var linkDone = '/dashboard/client/projects/completed?focus=' + p.id;
                var titleCell = p.status === 'completed'
                    ? '<a href="' + linkDone + '" class="fw-semibold text-decoration-none">' + escapeHtml(p.title) + '</a>'
                    : (p.status === 'open' || p.status === 'in_progress'
                        ? '<a href="' + linkActive + '" class="fw-semibold text-decoration-none">' + escapeHtml(p.title) + '</a>'
                        : '<strong>' + escapeHtml(p.title) + '</strong>');
                return '<tr class="' + rowHighlight(p.id) + '" id="proj-' + p.id + '">' +
                    '<td>' + titleCell + '</td>' +
                    '<td><span class="badge ' + DC.statusBadgeClass(p.status) + '">' + escapeHtml(p.status) + '</span></td>' +
                    '<td>' + DC.formatCurrency(p.budget_min) + ' – ' + DC.formatCurrency(p.budget_max) + '</td>' +
                    '<td>' + p.bids_count + '</td>' +
                    '<td><a class="btn btn-sm btn-outline-fh" href="/dashboard/client/projects/' + p.id + '/bids">Bids</a></td>' +
                    '</tr>';
            }).join('') || '<tr><td colspan="5" class="text-muted">No projects.</td></tr>';

            var focus = new URLSearchParams(window.location.search).get('focus');
            if (focus) {
                var row = document.getElementById('proj-' + focus);
                if (row) row.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        },

        tableActive: async function () {
            await DC.requireRole('client');
            var projects = await loadProjects();
            var list = projects.filter(function (p) {
                return p.status === 'open' || p.status === 'in_progress';
            });
            var tbody = document.querySelector('#tbl-active tbody');
            if (!tbody) return;
            tbody.innerHTML = list.map(function (p) {
                return '<tr class="' + rowHighlight(p.id) + '" id="proj-' + p.id + '">' +
                    '<td>' + escapeHtml(p.title) + '</td>' +
                    '<td><span class="badge ' + DC.statusBadgeClass(p.status) + '">' + escapeHtml(p.status) + '</span></td>' +
                    '<td>' + DC.formatCurrency(p.budget_min) + ' – ' + DC.formatCurrency(p.budget_max) + '</td>' +
                    '<td>' + p.bids_count + '</td>' +
                    '<td><a class="btn btn-sm btn-outline-fh" href="/dashboard/client/projects/' + p.id + '/bids">Manage</a></td>' +
                    '</tr>';
            }).join('') || '<tr><td colspan="5" class="text-muted">No active projects.</td></tr>';
            scrollFocus();
        },

        tableCompleted: async function () {
            await DC.requireRole('client');
            var projects = await loadProjects();
            var list = projects.filter(function (p) { return p.status === 'completed'; });
            var tbody = document.querySelector('#tbl-completed tbody');
            if (!tbody) return;
            tbody.innerHTML = list.map(function (p) {
                return '<tr class="' + rowHighlight(p.id) + '" id="proj-' + p.id + '">' +
                    '<td>' + escapeHtml(p.title) + '</td>' +
                    '<td>' + DC.formatCurrency(p.budget_max) + '</td>' +
                    '<td>' + DC.formatDate(p.created_at) + '</td>' +
                    '</tr>';
            }).join('') || '<tr><td colspan="3" class="text-muted">No completed projects yet.</td></tr>';
            scrollFocus();
        },

        projectNew: async function () {
            await DC.requireRole('client');
            var form = document.getElementById('formNewProject');
            if (!form) return;
            form.addEventListener('submit', async function (e) {
                e.preventDefault();
                var payload = {
                    title: document.getElementById('projectTitle').value,
                    description: document.getElementById('projectDescription').value,
                    budget_min: parseFloat(document.getElementById('budgetMin').value),
                    budget_max: parseFloat(document.getElementById('budgetMax').value),
                    required_skills: document.getElementById('requiredSkills').value,
                    category: document.getElementById('projectCategory').value
                };
                var res = await DC.authFetch('/client/projects', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });
                var data = await res.json();
                if (res.ok) {
                    DC.toast('Project posted successfully.', 'success');
                    window.location.href = '/dashboard/client/my-projects';
                } else {
                    DC.toast(data.error || 'Could not create project.', 'error');
                }
            });
        },

        projectBids: async function (projectId) {
            await DC.requireRole('client');
            var res = await DC.authFetch('/client/projects/' + projectId + '/bids');
            if (!res || !res.ok) {
                document.getElementById('bids-container').innerHTML = '<p class="text-danger">Could not load bids.</p>';
                return;
            }
            var bids = await res.json();
            var titleEl = document.getElementById('project-bids-title');
            var container = document.getElementById('bids-container');
            var pres = await DC.authFetch('/client/projects/' + projectId);
            if (pres && pres.ok) {
                var proj = await pres.json();
                if (titleEl) titleEl.textContent = proj.title;
            }
            container.innerHTML = bids.map(function (b) {
                return '<div class="card dash-card mb-3">' +
                    '<div class="card-body">' +
                    '<div class="d-flex flex-wrap justify-content-between gap-2">' +
                    '<div><h3 class="h6 mb-1">' + escapeHtml(b.student_name) + '</h3>' +
                    '<p class="small text-muted mb-0">Rating: ' + (b.student_rating || '—') + ' · ' + DC.formatCurrency(b.amount) + '</p></div>' +
                    '<span class="badge ' + DC.statusBadgeClass(b.status) + ' align-self-start">' + escapeHtml(b.status) + '</span></div>' +
                    '<p class="mt-3 mb-3">' + escapeHtml(b.proposal) + '</p>' +
                    '<div class="d-flex gap-2">' +
                    (b.status === 'pending' ? '<button type="button" class="btn btn-success btn-sm btn-accept" data-bid="' + b.id + '">Accept</button>' +
                        '<button type="button" class="btn btn-outline-danger btn-sm btn-reject" data-bid="' + b.id + '">Reject</button>' : '') +
                    '</div></div></div>';
            }).join('') || '<p class="text-muted">No bids yet.</p>';

            container.querySelectorAll('.btn-accept').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    acceptBid(btn.getAttribute('data-bid'));
                });
            });
            container.querySelectorAll('.btn-reject').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    rejectBid(btn.getAttribute('data-bid'));
                });
            });
        },

        profilePage: async function () {
            await DC.requireRole('client');
            var meRes = await DC.authFetch('/auth/me');
            if (!meRes || !meRes.ok) return;
            var me = await meRes.json();
            document.getElementById('client-email').textContent = me.email;

            var res = await DC.authFetch('/client/profile');
            if (!res || !res.ok) {
                DC.toast('Could not load profile.', 'error');
                return;
            }
            var d = await res.json();
            document.getElementById('companyName').value = d.company || '';
            document.getElementById('companyDesc').value = d.description || '';
            document.getElementById('client-verified').innerHTML = d.verified
                ? '<span class="badge bg-light text-success">Verified</span>'
                : '<span class="badge bg-light text-warning">Not verified</span>';

            document.getElementById('formClientProfile').addEventListener('submit', async function (e) {
                e.preventDefault();
                var put = await DC.authFetch('/client/profile', {
                    method: 'PUT',
                    body: JSON.stringify({
                        company: document.getElementById('companyName').value,
                        description: document.getElementById('companyDesc').value
                    })
                });
                var out = await put.json();
                if (put.ok) DC.toast('Profile updated.', 'success');
                else DC.toast(out.error || 'Save failed.', 'error');
            });
        }
    };

    function scrollFocus() {
        var focus = new URLSearchParams(window.location.search).get('focus');
        if (focus) {
            var row = document.getElementById('proj-' + focus);
            if (row) row.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    function escapeHtml(s) {
        if (!s) return '';
        var d = document.createElement('div');
        d.textContent = s;
        return d.innerHTML;
    }

    async function completeProject(pid) {
        var res = await DC.authFetch('/client/projects/' + pid + '/complete', { method: 'POST' });
        var data = await res.json();
        if (res.ok) {
            DC.toast('Project marked complete.', 'success');
            window.location.reload();
        } else {
            DC.toast(data.error || 'Failed.', 'error');
        }
    }

    async function acceptBid(bidId) {
        var res = await DC.authFetch('/client/bids/' + bidId + '/accept', { method: 'POST' });
        var data = await res.json();
        if (res.ok) {
            DC.toast('Bid accepted.', 'success');
            window.location.reload();
        } else {
            DC.toast(data.error || 'Failed.', 'error');
        }
    }

    async function rejectBid(bidId) {
        var res = await DC.authFetch('/client/bids/' + bidId + '/reject', { method: 'POST' });
        if (res.ok) {
            DC.toast('Bid rejected.', 'success');
            window.location.reload();
        }
    }
})();
