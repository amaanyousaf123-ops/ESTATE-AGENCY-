document.addEventListener('DOMContentLoaded', () => {
    // --- State ---
    let token = null;
    let currentUser = null;
    let currentRole = null;

    // --- DOM Elements ---
    const loginScreen = document.getElementById('login-screen');
    const dashboardScreen = document.getElementById('dashboard-screen');
    const loginForm = document.getElementById('login-form');
    const loginError = document.getElementById('login-error');
    const navLinks = document.querySelectorAll('.nav-links li');
    const views = document.querySelectorAll('.view');
    const pageTitle = document.getElementById('page-title');
    const currentUserSpan = document.getElementById('current-user');
    const logoutBtn = document.getElementById('logout-btn');
    
    const btnAddProperty = document.getElementById('btn-add-property');
    const modalAddProperty = document.getElementById('modal-add-property');
    const closeBtn = document.querySelector('.close-modal');
    const formAddProperty = document.getElementById('form-add-property');

    // --- Auth ---
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            if (res.ok) {
                token = data.token;
                currentUser = data.name;
                currentRole = data.role;
                currentUserSpan.textContent = currentUser;
                
                loginScreen.classList.remove('active');
                setTimeout(() => dashboardScreen.classList.add('active'), 400);
                
                loadDashboard();
            } else {
                loginError.textContent = data.error || 'Login failed';
            }
        } catch (err) {
            loginError.textContent = 'Server error. Is the backend running?';
        }
    });

    logoutBtn.addEventListener('click', () => {
        token = null;
        dashboardScreen.classList.remove('active');
        setTimeout(() => loginScreen.classList.add('active'), 400);
    });

    // --- Navigation ---
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            // Update active link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Update title
            pageTitle.textContent = link.textContent;
            
            // Show target view
            const targetId = link.getAttribute('data-target');
            views.forEach(v => v.classList.remove('active'));
            document.getElementById(targetId).classList.add('active');
            
            // Load data for view
            if (targetId === 'view-dashboard') loadDashboard();
            else if (targetId === 'view-properties') loadProperties();
            else if (targetId === 'view-rentals') loadRentals();
            else if (targetId === 'view-sales') loadSales();
            else if (targetId === 'view-maintenance') loadMaintenance();
        });
    });

    // --- Load Data ---
    async function apiGet(endpoint) {
        const res = await fetch(endpoint);
        return await res.json();
    }

    async function loadDashboard() {
        const data = await apiGet('/api/dashboard');
        const grid = document.getElementById('dashboard-stats');
        grid.innerHTML = `
            <div class="stat-card"><h3>Total Properties</h3><div class="value">${data.total_properties}</div></div>
            <div class="stat-card"><h3>Vacant Properties</h3><div class="value">${data.vacant}</div></div>
            <div class="stat-card"><h3>Rented</h3><div class="value">${data.rented}</div></div>
            <div class="stat-card"><h3>Active Leases</h3><div class="value">${data.active_leases}</div></div>
            <div class="stat-card"><h3>Open Maintenance</h3><div class="value">${data.open_maintenance}</div></div>
        `;
    }

    async function loadProperties() {
        const data = await apiGet('/api/properties');
        const tbody = document.getElementById('properties-tbody');
        tbody.innerHTML = data.map(p => `
            <tr>
                <td>${p.id}</td>
                <td>${p.block}-${p.unit_number}</td>
                <td style="text-transform: capitalize">${p.type}</td>
                <td>${p.size}</td>
                <td><span class="badge ${p.status}">${p.status.replace('_', ' ')}</span></td>
            </tr>
        `).join('');
    }

    async function loadRentals() {
        const data = await apiGet('/api/rentals');
        const tbody = document.getElementById('rentals-tbody');
        tbody.innerHTML = data.map(r => `
            <tr>
                <td>${r.unit_number}</td>
                <td>${r.tenant_name}</td>
                <td>${r.lease_end}</td>
                <td>Rs. ${r.rent_amount.toLocaleString()}</td>
                <td><span class="badge ${r.status}">${r.status}</span></td>
            </tr>
        `).join('');
    }

    async function loadSales() {
        const data = await apiGet('/api/sales');
        const tbody = document.getElementById('sales-tbody');
        tbody.innerHTML = data.map(s => `
            <tr>
                <td>${s.unit_number}</td>
                <td>${s.buyer_name}</td>
                <td>Rs. ${s.sale_price.toLocaleString()}</td>
                <td>${s.transaction_date}</td>
                <td><span class="badge ${s.status}">${s.status}</span></td>
            </tr>
        `).join('');
    }

    async function loadMaintenance() {
        const data = await apiGet('/api/maintenance');
        const tbody = document.getElementById('maintenance-tbody');
        tbody.innerHTML = data.map(m => `
            <tr>
                <td>${m.unit_number}</td>
                <td>${m.issue_description}</td>
                <td>${m.reported_by}</td>
                <td>${m.date_reported}</td>
                <td><span class="badge ${m.status}">${m.status.replace('_', ' ')}</span></td>
            </tr>
        `).join('');
    }

    // --- Add Property Modal ---
    btnAddProperty.addEventListener('click', () => {
        if (currentRole === 'maintenance') {
            alert('Maintenance role cannot add properties.');
            return;
        }
        modalAddProperty.classList.add('active');
    });

    closeBtn.addEventListener('click', () => modalAddProperty.classList.remove('active'));
    window.addEventListener('click', (e) => {
        if(e.target === modalAddProperty) modalAddProperty.classList.remove('active');
    });

    formAddProperty.addEventListener('submit', async (e) => {
        e.preventDefault();
        const block = document.getElementById('prop-block').value;
        const unit = document.getElementById('prop-unit').value;
        const type = document.getElementById('prop-type').value;
        const size = document.getElementById('prop-size').value;

        await fetch('/api/properties', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ block, unit_number: unit, type, size })
        });

        modalAddProperty.classList.remove('active');
        formAddProperty.reset();
        
        // Refresh properties view if active
        if(document.getElementById('view-properties').classList.contains('active')) {
            loadProperties();
        } else {
            // Or just load dashboard if that's active
            loadDashboard();
        }
    });
});
