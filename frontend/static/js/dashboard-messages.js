(function () {
    'use strict';

    var DC = window.DashboardCommon;

    function escapeHtml(s) {
        if (!s) return '';
        var d = document.createElement('div');
        d.textContent = s;
        return d.innerHTML;
    }

    function formatTime(iso) {
        if (!iso) return '';
        var d = new Date(iso);
        return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    }

    window.DashboardMessages = {
        init: async function (opts) {
            var role = opts && opts.role;
            if (!role) return;
            await DC.requireRole(role);
            var meRes = await DC.authFetch('/auth/me');
            if (!meRes || !meRes.ok) return;
            var me = await meRes.json();
            var meId = me.id;

            var selectedPartnerId = null;
            var seenIds = new Set();
            var contactsById = {};

            var elList = document.getElementById('msg-contact-list');
            var elEmpty = document.getElementById('msg-contacts-empty');
            var elTitle = document.getElementById('msg-thread-title');
            var elSub = document.getElementById('msg-thread-sub');
            var elBody = document.getElementById('msg-thread-body');
            var elInput = document.getElementById('msg-input');
            var elSend = document.getElementById('msg-send');
            var elForm = document.getElementById('msg-form');

            function threadPartnerLabel() {
                var c = contactsById[selectedPartnerId];
                return c ? (c.label || c.email || 'User') : '';
            }

            function isForActiveThread(data) {
                if (selectedPartnerId == null) return false;
                var a = data.sender_id;
                var b = data.receiver_id;
                return (a === meId && b === selectedPartnerId) || (a === selectedPartnerId && b === meId);
            }

            function appendBubble(m) {
                if (seenIds.has(m.id)) return;
                seenIds.add(m.id);
                var mine = m.sender_id === meId;
                var wrap = document.createElement('div');
                wrap.className = 'd-flex ' + (mine ? 'justify-content-end' : 'justify-content-start');
                var bubble = document.createElement('div');
                bubble.className = 'message-bubble ' + (mine ? 'message-sent' : 'message-received');
                bubble.innerHTML =
                    '<div>' + escapeHtml(m.content) + '</div>' +
                    '<div class="message-time">' + escapeHtml(formatTime(m.timestamp)) + '</div>';
                wrap.appendChild(bubble);
                elBody.appendChild(wrap);
                elBody.scrollTop = elBody.scrollHeight;
            }

            function setComposerEnabled(on) {
                elInput.disabled = !on;
                elSend.disabled = !on;
                if (!on) elInput.value = '';
            }

            function clearThread() {
                elBody.innerHTML = '';
                seenIds.clear();
            }

            async function openThread(partnerId) {
                selectedPartnerId = partnerId;
                clearThread();
                elTitle.textContent = threadPartnerLabel() || 'Conversation';
                elSub.textContent = contactsById[partnerId] ? (contactsById[partnerId].email || '') : '';
                setComposerEnabled(true);

                var res = await DC.authFetch('/chat/messages/' + partnerId);
                var data = res && res.ok ? await res.json() : null;
                if (!res || !res.ok) {
                    DC.toast((data && data.error) || 'Could not load messages.', 'error');
                    setComposerEnabled(false);
                    return;
                }
                data.forEach(appendBubble);
                elBody.scrollTop = elBody.scrollHeight;
                renderContactList();
            }

            function renderContactList(rows, convMap) {
                convMap = convMap || {};
                if (!elList) return;
                elList.innerHTML = '';
                if (!rows.length) {
                    elEmpty.classList.remove('d-none');
                    return;
                }
                elEmpty.classList.add('d-none');
                rows.forEach(function (c) {
                    var conv = convMap[c.user_id] || {};
                    var unread = conv.unread_count || 0;
                    var last = conv.last_message || '';
                    var short = last.length > 72 ? last.slice(0, 72) + '…' : last;
                    var a = document.createElement('button');
                    a.type = 'button';
                    a.className =
                        'list-group-item list-group-item-action text-start py-3 msg-contact-row' +
                        (selectedPartnerId === c.user_id ? ' active' : '');
                    a.dataset.userId = String(c.user_id);
                    a.innerHTML =
                        '<div class="d-flex justify-content-between align-items-start gap-2">' +
                        '<span class="fw-semibold">' + escapeHtml(c.label || c.email) + '</span>' +
                        (unread > 0
                            ? '<span class="badge bg-danger rounded-pill">' + unread + '</span>'
                            : '') +
                        '</div>' +
                        '<div class="small text-muted text-truncate mt-1">' +
                        (short ? escapeHtml(short) : '<em>No messages yet</em>') +
                        '</div>';
                    elList.appendChild(a);
                });

                elList.querySelectorAll('.msg-contact-row').forEach(function (btn) {
                    btn.addEventListener('click', function () {
                        var id = parseInt(btn.getAttribute('data-user-id'), 10);
                        openThread(id);
                    });
                });
            }

            async function loadSidebar() {
                var cRes = await DC.authFetch('/chat/contacts');
                var vRes = await DC.authFetch('/chat/conversations');
                var contacts = cRes && cRes.ok ? await cRes.json() : [];
                var convs = vRes && vRes.ok ? await vRes.json() : [];
                contactsById = {};
                contacts.forEach(function (c) {
                    contactsById[c.user_id] = c;
                });
                var convMap = {};
                convs.forEach(function (x) {
                    convMap[x.user_id] = x;
                });
                renderContactList(contacts, convMap);
            }

            function onSocketMessage(data) {
                if (!data || data.id == null) return;
                if (isForActiveThread(data)) {
                    appendBubble({
                        id: data.id,
                        sender_id: data.sender_id,
                        receiver_id: data.receiver_id,
                        content: data.content,
                        timestamp: data.timestamp
                    });
                }
                loadSidebar();
            }

            var token = DC.getToken();
            if (token && window.io) {
                if (!window.__fhInboxSocket) {
                    window.__fhInboxSocket = window.io(window.location.origin, { auth: { token: token } });
                }
                window.__fhInboxSocket.off('receive_message');
                window.__fhInboxSocket.on('receive_message', onSocketMessage);
            }

            elForm.addEventListener('submit', async function (e) {
                e.preventDefault();
                if (selectedPartnerId == null) return;
                var text = (elInput.value || '').trim();
                if (!text) return;
                elSend.disabled = true;
                var res = await DC.authFetch('/chat/messages', {
                    method: 'POST',
                    body: JSON.stringify({ receiver_id: selectedPartnerId, content: text })
                });
                var out = {};
                try {
                    out = await res.json();
                } catch (err) {
                    out = {};
                }
                elSend.disabled = false;
                if (res && res.ok) {
                    elInput.value = '';
                    appendBubble({
                        id: out.id,
                        sender_id: out.sender_id,
                        receiver_id: out.receiver_id,
                        content: out.content,
                        timestamp: out.timestamp
                    });
                    loadSidebar();
                } else {
                    DC.toast((out && out.error) || 'Send failed.', 'error');
                }
            });

            await loadSidebar();
            elTitle.textContent = 'Select a conversation';
            elSub.textContent = '';
            setComposerEnabled(false);
        }
    };
})();
