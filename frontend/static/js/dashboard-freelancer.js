(function () {
    'use strict';

    var DC = window.DashboardCommon;

    function escapeHtml(s) {
        if (!s) return '';
        var d = document.createElement('div');
        d.textContent = s;
        return d.innerHTML;
    }

    function stars(n) {
        n = Math.round(Number(n) || 0);
        var out = '';
        for (var i = 0; i < 5; i++) {
            out += i < n ? '<i class="fas fa-star text-warning"></i>' : '<i class="far fa-star text-warning"></i>';
        }
        return out;
    }

    window.FreelancerDash = {
        overview: async function () {
            await DC.requireRole('student');
            var pr = await DC.authFetch('/student/profile');
            if (!pr || !pr.ok) return;
            var profile = await pr.json();

            document.getElementById('ov-rating').textContent = (profile.avg_rating != null ? Number(profile.avg_rating).toFixed(1) : '—');
            document.getElementById('ov-projects').textContent = profile.total_projects != null ? profile.total_projects : '0';

            var br = await DC.authFetch('/student/bids');
            var bids = br && br.ok ? await br.json() : [];
            document.getElementById('ov-bids').textContent = bids.length;

            var rec = await DC.authFetch('/student/recommendations');
            var recData = rec && rec.ok ? await rec.json() : [];
            document.getElementById('ov-reco-count').textContent = recData.length;

            var recent = bids.slice(0, 4);
            var el = document.getElementById('ov-recent-bids');
            if (el) {
                el.innerHTML = recent.map(function (b) {
                    return '<div class="d-flex justify-content-between border-bottom py-2">' +
                        '<div><span class="fw-semibold">' + escapeHtml(b.project_title) + '</span><br><small class="text-muted">' + DC.formatDate(b.created_at) + '</small></div>' +
                        '<span class="badge ' + DC.statusBadgeClass(b.status) + '">' + escapeHtml(b.status) + '</span></div>';
                }).join('') || '<p class="text-muted small mb-0">No bids yet.</p>';
            }

            var recBox = document.getElementById('ov-reco-preview');
            if (recBox) {
                recBox.innerHTML = recData.slice(0, 3).map(function (p) {
                    return '<div class="border-bottom py-2"><strong>' + escapeHtml(p.title) + '</strong><br><small class="text-muted">' + DC.formatCurrency(p.budget_max) + '</small></div>';
                }).join('') || '<p class="text-muted small">Add skills to your profile for AI matches.</p>';
            }
        },

        projectsBrowse: async function () {
            await DC.requireRole('student');
            var res = await DC.authFetch('/student/projects/browse?page=1&per_page=100');
            if (!res || !res.ok) return;
            var data = await res.json();
            var projects = data.projects || [];
            var tbody = document.querySelector('#tbl-browse tbody');
            if (tbody) {
                tbody.innerHTML = projects.map(function (p) {
                    var desc = p.description || '';
                    var short = desc.length > 90 ? escapeHtml(desc.slice(0, 90)) + '…' : escapeHtml(desc);
                    return '<tr><td><strong>' + escapeHtml(p.title) + '</strong><br><small class="text-muted">' + short + '</small></td>' +
                        '<td>' + escapeHtml(p.category || '—') + '</td>' +
                        '<td>' + DC.formatCurrency(p.budget_min) + ' – ' + DC.formatCurrency(p.budget_max) + '</td>' +
                        '<td>' + DC.formatDate(p.created_at) + '</td>' +
                        '<td><button type="button" class="btn btn-sm btn-fh btn-bid" data-id="' + p.id + '">Bid</button></td></tr>';
                }).join('') || '<tr><td colspan="5" class="text-muted">No open projects.</td></tr>';
                bindBidButtons(tbody);
            }
        },

        bidsAll: async function () {
            await DC.requireRole('student');
            var res = await DC.authFetch('/student/bids');
            if (!res || !res.ok) return;
            var bids = await res.json();
            var tbody = document.querySelector('#tbl-bids tbody');
            if (tbody) {
                tbody.innerHTML = bids.map(function (b) {
                    return '<tr><td>' + escapeHtml(b.project_title) + '</td>' +
                        '<td>' + DC.formatCurrency(b.amount) + '</td>' +
                        '<td><span class="badge ' + DC.statusBadgeClass(b.status) + '">' + escapeHtml(b.status) + '</span></td>' +
                        '<td>' + DC.formatDate(b.created_at) + '</td>' +
                        '<td><small>' + escapeHtml((b.proposal || '').slice(0, 60)) + '…</small></td></tr>';
                }).join('') || '<tr><td colspan="5" class="text-muted">No bids.</td></tr>';
            }
        },

        bidsRecent: async function () {
            await DC.requireRole('student');
            var res = await DC.authFetch('/student/bids');
            if (!res || !res.ok) return;
            var bids = await res.json();
            var recent = bids.slice(0, 15);
            var tbody = document.querySelector('#tbl-bids-recent tbody');
            if (tbody) {
                tbody.innerHTML = recent.map(function (b) {
                    return '<tr><td>' + escapeHtml(b.project_title) + '</td>' +
                        '<td>' + DC.formatCurrency(b.amount) + '</td>' +
                        '<td><span class="badge ' + DC.statusBadgeClass(b.status) + '">' + escapeHtml(b.status) + '</span></td>' +
                        '<td>' + DC.formatDate(b.created_at) + '</td></tr>';
                }).join('') || '<tr><td colspan="4" class="text-muted">No recent bids.</td></tr>';
            }
        },

        ratingPage: async function () {
            await DC.requireRole('student');
            var res = await DC.authFetch('/student/profile');
            if (!res || !res.ok) return;
            var profile = await res.json();
            var avg = profile.avg_rating != null ? Number(profile.avg_rating) : 0;
            document.getElementById('rating-big').textContent = avg.toFixed(1);
            document.getElementById('rating-stars').innerHTML = stars(Math.round(avg));
            document.getElementById('rating-projects').textContent = profile.total_projects != null ? profile.total_projects : '0';

            var rv = await DC.authFetch('/student/reviews');
            var reviews = rv && rv.ok ? await rv.json() : [];
            document.getElementById('rating-count').textContent = reviews.length;
        },

        reviewsPage: async function () {
            await DC.requireRole('student');
            var res = await DC.authFetch('/student/reviews');
            if (!res || !res.ok) return;
            var reviews = await res.json();
            var tbody = document.querySelector('#tbl-reviews tbody');
            if (tbody) {
                tbody.innerHTML = reviews.map(function (r) {
                    return '<tr><td>' + escapeHtml(r.project_title) + '</td>' +
                        '<td>' + stars(r.rating) + ' <span class="ms-1">' + r.rating + '/5</span></td>' +
                        '<td>' + escapeHtml(r.comment || '—') + '</td>' +
                        '<td><small class="text-muted">' + escapeHtml(r.reviewer_email || '') + '</small></td>' +
                        '<td>' + DC.formatDate(r.created_at) + '</td></tr>';
                }).join('') || '<tr><td colspan="5" class="text-muted">No reviews yet.</td></tr>';
            }
        },

        recommended: async function () {
            await DC.requireRole('student');
            var res = await DC.authFetch('/student/recommendations');
            if (!res || !res.ok) return;
            var list = await res.json();
            var grid = document.getElementById('reco-grid');
            if (!grid) return;
            if (!list.length) {
                grid.innerHTML = '<div class="col-12"><div class="alert border dash-card mb-0" style="background:var(--fh-primary-soft);color:var(--fh-primary-hover);border-color:var(--fh-primary)!important;">No recommendations yet. Add skills to your profile so we can match you to projects.</div></div>';
                return;
            }
            grid.innerHTML = list.map(function (p) {
                var pid = p.project_id || p.id;
                var score = p.similarity_score != null ? (Number(p.similarity_score) * 100).toFixed(0) + '% match' : '';
                var desc = p.description || '';
                var descHtml = desc.length > 160 ? escapeHtml(desc.slice(0, 160)) + '…' : escapeHtml(desc);
                return '<div class="col-md-6 col-xl-4 d-flex">' +
                    '<div class="card dash-card dash-card--accent fh-hub-card flex-fill">' +
                    '<div class="card-body d-flex flex-column">' +
                    '<span class="fh-skill-chip mb-2 align-self-start"><i class="fas fa-robot me-1"></i>AI pick</span>' +
                    '<h3 class="h5">' + escapeHtml(p.title) + '</h3>' +
                    '<p class="small text-muted flex-grow-1">' + descHtml + '</p>' +
                    '<p class="small mb-2"><strong>Budget:</strong> ' + DC.formatCurrency(p.budget_max) + '</p>' +
                    '<p class="small text-fh-primary mb-3 fw-semibold">' + score + '</p>' +
                    '<button type="button" class="btn btn-sm btn-fh btn-bid mt-auto align-self-start" data-id="' + pid + '">Submit bid</button>' +
                    '</div></div></div>';
            }).join('');
            bindBidButtons(grid);
        },

        profilePage: async function () {
            await DC.requireRole('student');
            var meRes = await DC.authFetch('/auth/me');
            if (!meRes || !meRes.ok) return;
            var me = await meRes.json();
            document.getElementById('fl-email').textContent = me.email;

            async function loadProfile() {
                var res = await DC.authFetch('/student/profile');
                if (!res || !res.ok) return;
                var d = await res.json();
                document.getElementById('fl-name').value = d.name || '';
                document.getElementById('fl-college').value = d.college || '';
                document.getElementById('fl-year').value = d.year || '';
                document.getElementById('fl-bio').value = d.bio || '';
                document.getElementById('fl-portfolio').value = d.portfolio_url || '';
                document.getElementById('fl-avg').textContent = d.avg_rating != null ? Number(d.avg_rating).toFixed(1) : '—';
                document.getElementById('fl-done').textContent = d.total_projects != null ? String(d.total_projects) : '0';
                var ap = document.getElementById('fl-approved');
                ap.textContent = d.is_approved ? 'Approved' : 'Pending';
                ap.className = 'badge ms-1 ' + (d.is_approved ? 'bg-light text-success' : 'bg-light text-warning');

                var skillsEl = document.getElementById('fl-skills');
                if (d.skills && d.skills.length) {
                    skillsEl.innerHTML = d.skills.map(function (s) {
                        return '<span class="fh-skill-chip">' + escapeHtml(s.name) + ' · L' + s.proficiency + '</span>';
                    }).join('');
                } else {
                    skillsEl.innerHTML = '<span class="text-muted small">No skills yet.</span>';
                }

                var st = document.getElementById('fl-resume-status');
                var btnDl = document.getElementById('fl-resume-download');
                var btnRm = document.getElementById('fl-resume-remove');
                if (st && btnDl && btnRm) {
                    if (d.has_resume && d.resume_original_name) {
                        st.innerHTML = 'Current file: <strong>' + escapeHtml(d.resume_original_name) + '</strong>';
                        btnDl.classList.remove('d-none');
                        btnRm.classList.remove('d-none');
                    } else {
                        st.innerHTML = '<span class="text-muted">No file uploaded.</span>';
                        btnDl.classList.add('d-none');
                        btnRm.classList.add('d-none');
                    }
                }
            }

            await loadProfile();

            document.getElementById('formFreelancerProfile').addEventListener('submit', async function (e) {
                e.preventDefault();
                var put = await DC.authFetch('/student/profile', {
                    method: 'PUT',
                    body: JSON.stringify({
                        name: document.getElementById('fl-name').value,
                        college: document.getElementById('fl-college').value,
                        year: document.getElementById('fl-year').value,
                        bio: document.getElementById('fl-bio').value,
                        portfolio_url: document.getElementById('fl-portfolio').value
                    })
                });
                var out = await put.json();
                if (put.ok) {
                    DC.toast('Profile saved.', 'success');
                    await loadProfile();
                } else {
                    DC.toast(out.error || 'Save failed.', 'error');
                }
            });

            document.getElementById('formAddSkill').addEventListener('submit', async function (e) {
                e.preventDefault();
                var post = await DC.authFetch('/student/skills', {
                    method: 'POST',
                    body: JSON.stringify({
                        skill_name: document.getElementById('skillName').value,
                        proficiency: parseInt(document.getElementById('skillProf').value, 10) || 3
                    })
                });
                var out = await post.json();
                if (post.ok) {
                    DC.toast('Skill added.', 'success');
                    document.getElementById('skillName').value = '';
                    await loadProfile();
                } else {
                    DC.toast(out.error || 'Could not add skill.', 'error');
                }
            });

            var btnUp = document.getElementById('fl-resume-upload');
            var btnDl = document.getElementById('fl-resume-download');
            var btnRm = document.getElementById('fl-resume-remove');
            var fileInput = document.getElementById('fl-resume-file');

            if (btnUp && fileInput) {
                btnUp.addEventListener('click', async function () {
                    var f = fileInput.files && fileInput.files[0];
                    if (!f) {
                        DC.toast('Choose a file first.', 'error');
                        return;
                    }
                    var fd = new FormData();
                    fd.append('file', f);
                    var res = await DC.authFetch('/student/resume', { method: 'POST', body: fd });
                    var out = {};
                    try {
                        out = await res.json();
                    } catch (err) {
                        out = {};
                    }
                    if (res && res.ok) {
                        DC.toast('Resume uploaded.', 'success');
                        fileInput.value = '';
                        await loadProfile();
                    } else {
                        DC.toast(out.error || 'Upload failed.', 'error');
                    }
                });
            }

            if (btnDl) {
                btnDl.addEventListener('click', async function (e) {
                    e.preventDefault();
                    var res = await DC.authFetch('/student/resume/download');
                    if (!res || !res.ok) {
                        var err = {};
                        try {
                            err = await res.json();
                        } catch (x) {
                            err = {};
                        }
                        DC.toast(err.error || 'Download failed.', 'error');
                        return;
                    }
                    var blob = await res.blob();
                    var cd = res.headers.get('Content-Disposition') || '';
                    var name = 'resume';
                    var m = /filename\*?=(?:UTF-8''|)([^;\n]+)/i.exec(cd);
                    if (m) {
                        name = decodeURIComponent(m[1].replace(/['"]/g, '').trim());
                    }
                    var url = URL.createObjectURL(blob);
                    var a = document.createElement('a');
                    a.href = url;
                    a.download = name;
                    a.click();
                    URL.revokeObjectURL(url);
                });
            }

            if (btnRm) {
                btnRm.addEventListener('click', async function () {
                    if (!window.confirm('Remove your resume from the platform?')) return;
                    var res = await DC.authFetch('/student/resume', { method: 'DELETE' });
                    var out = {};
                    try {
                        out = await res.json();
                    } catch (err) {
                        out = {};
                    }
                    if (res && res.ok) {
                        DC.toast('Resume removed.', 'success');
                        await loadProfile();
                    } else {
                        DC.toast(out.error || 'Could not remove resume.', 'error');
                    }
                });
            }
        }
    };

    function bindBidButtons(root) {
        if (!root) return;
        root.querySelectorAll('.btn-bid').forEach(function (btn) {
            btn.addEventListener('click', function () {
                openBidModal(btn.getAttribute('data-id'));
            });
        });
    }

    function openBidModal(projectId) {
        var html = '<div class="modal fade" id="bidModal" tabindex="-1">' +
            '<div class="modal-dialog"><div class="modal-content">' +
            '<div class="modal-header"><h5 class="modal-title">Submit bid</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>' +
            '<div class="modal-body">' +
            '<form id="bidModalForm">' +
            '<div class="mb-3"><label class="form-label">Amount (₹)</label><input type="number" class="form-control" id="bidAmount" required min="1" step="1"></div>' +
            '<div class="mb-3"><label class="form-label">Proposal</label><textarea class="form-control" id="bidProposal" rows="4" required></textarea></div>' +
            '<button type="submit" class="btn btn-fh">Submit</button>' +
            '</form></div></div></div></div>';
        var wrap = document.createElement('div');
        wrap.innerHTML = html;
        document.body.appendChild(wrap);
        var modalEl = document.getElementById('bidModal');
        var modal = new bootstrap.Modal(modalEl);
        modalEl.addEventListener('hidden.bs.modal', function cleanup() {
            wrap.remove();
        }, { once: true });
        modal.show();
        document.getElementById('bidModalForm').addEventListener('submit', async function (e) {
            e.preventDefault();
            var amount = parseFloat(document.getElementById('bidAmount').value);
            var proposal = document.getElementById('bidProposal').value;
            var res = await DC.authFetch('/student/projects/' + projectId + '/bid', {
                method: 'POST',
                body: JSON.stringify({ amount: amount, proposal: proposal })
            });
            var data = await res.json();
            if (res.ok) {
                DC.toast('Bid submitted.', 'success');
                modal.hide();
                if (window.location.pathname.indexOf('/bids') !== -1) {
                    setTimeout(function () { window.location.reload(); }, 400);
                }
            } else {
                DC.toast(data.error || 'Could not submit bid.', 'error');
            }
        });
    }
})();
