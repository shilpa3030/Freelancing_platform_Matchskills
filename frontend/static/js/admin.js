// Admin Dashboard Functions
function loadAdminDashboard() {
    document.getElementById('main-content').innerHTML = `
        <div class="container py-5">
            <h2 class="mb-4">Admin Dashboard</h2>
            <div class="card dashboard-card">
                <h4>Platform Statistics</h4>
                <div id="admin-stats"></div>
            </div>
            
            <div class="card dashboard-card mt-4">
                <h4>User Management</h4>
                <div id="users-list"></div>
            </div>
        </div>
    `;
    
    loadAdminStats();
    loadUsers();
}

function loadAdminStats() {
    fetch(`${API_URL}/admin/stats`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById('admin-stats').innerHTML = `
            <div class="row">
                <div class="col-md-3">
                    <div class="stat-box">
                        <div class="stat-number">${data.total_projects}</div>
                        <div class="stat-label">Total Projects</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-box">
                        <div class="stat-number">${data.total_students}</div>
                        <div class="stat-label">Total Students</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-box">
                        <div class="stat-number">${data.active_projects}</div>
                        <div class="stat-label">Active Projects</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-box">
                        <div class="stat-number">${formatCurrency(data.avg_project_value)}</div>
                        <div class="stat-label">Avg Project Value</div>
                    </div>
                </div>
            </div>
        `;
    });
}

function loadUsers() {
    fetch(`${API_URL}/admin/users`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
    })
    .then(res => res.json())
    .then(users => {
        const container = document.getElementById('users-list');
        container.innerHTML = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(u => `
                        <tr>
                            <td>${u.email}</td>
                            <td>${u.role}</td>
                            <td>${u.is_active ? 'Active' : 'Inactive'}</td>
                            <td>
                                ${u.role === 'student' && !u.is_approved ? 
                                    `<button class="btn btn-sm btn-success-custom" onclick="approveStudent(${u.id})">Approve</button>` : 
                                    ''}
                                ${u.is_active ? 
                                    `<button class="btn btn-sm btn-danger-custom" onclick="deactivateUser(${u.id})">Deactivate</button>` :
                                    `<button class="btn btn-sm btn-success-custom" onclick="activateUser(${u.id})">Activate</button>`}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    });
}

function approveStudent(userId) {
    fetch(`${API_URL}/admin/students/approve/${userId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${authToken}` }
    })
    .then(res => res.json())
    .then(data => {
        showNotification('Student approved!', 'success');
        loadUsers();
    });
}

function deactivateUser(userId) {
    fetch(`${API_URL}/admin/users/${userId}/deactivate`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${authToken}` }
    })
    .then(res => res.json())
    .then(data => {
        showNotification('User deactivated', 'success');
        loadUsers();
    });
}

function activateUser(userId) {
    fetch(`${API_URL}/admin/users/${userId}/activate`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${authToken}` }
    })
    .then(res => res.json())
    .then(data => {
        showNotification('User activated', 'success');
        loadUsers();
    });
}
