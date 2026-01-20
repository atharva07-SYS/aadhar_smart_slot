const API_BASE = '/api';

// --- AUTHENTICATION ---
let currentUser = null;

function checkAuth() {
    const token = localStorage.getItem('admin_token');
    const region = localStorage.getItem('admin_region');
    if (token) {
        currentUser = { token, region };
        document.getElementById('loginOverlay').style.display = 'none';
        document.getElementById('adminDashboard').style.display = 'block';
        document.getElementById('regionBadge').innerText = `Region: ${region}`;
        loadAdminData(); // Initial Load
    }
}

async function adminLogin(e) {
    e.preventDefault();
    const u = document.getElementById('admin_user').value;
    const p = document.getElementById('admin_pass').value;

    try {
        const res = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: u, password: p })
        });
        const data = await res.json();

        if (data.success) {
            localStorage.setItem('admin_token', data.token);
            localStorage.setItem('admin_region', data.region);
            checkAuth();
            showToast("Login Successful");
        } else {
            alert(data.message);
        }
    } catch (err) { alert("Login failed"); }
}

function logout() {
    localStorage.removeItem('admin_token');
    location.reload();
}

// --- CITIZEN: BOOKING ---
async function bookAppointment(event) {
    event.preventDefault();

    // UI Loading State
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.innerText = "Processing...";
    submitBtn.disabled = true;

    // Gather V2 Data
    const payload = {
        name: document.getElementById('name').value,
        phone: document.getElementById('user_phone').value,
        age: document.getElementById('user_age').value,
        request_type: document.getElementById('request_type').value,
        user_type: "Scheduled", // Default as per new requirement
        city: document.getElementById('city').value,
        pincode: document.getElementById('pincode').value
    };

    try {
        const res = await fetch(`${API_BASE}/book_appointment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await res.json();

        if (result.success) {
            const d = result.data;
            // Store for receipt
            lastBookingDetails = { ...d, center_name: result.center_name };

            document.getElementById('res_id').innerText = d.request_id;
            document.getElementById('res_center').innerText = result.center_name;
            document.getElementById('res_date').innerText = d.assigned_date;
            document.getElementById('res_time').innerText = d.assigned_time_slot;

            document.getElementById('bookingSection').style.display = 'none';
            document.getElementById('successView').style.display = 'block';

            showToast(`SMS Sent to ${payload.phone}`);
        } else {
            alert(result.message);
        }

    } catch (err) { alert("Error: " + err.message); }
    finally {
        submitBtn.innerText = "Find & Book Slot";
        submitBtn.disabled = false;
    }
}

let lastBookingDetails = null;

function downloadSlip() {
    if (!lastBookingDetails) return;

    const d = lastBookingDetails;
    const content = `
        UIDAI APPOINTMENT SLIP
        ----------------------
        Request ID : ${d.request_id}
        Name       : ${d.name || 'Citizen'}

        Center     : ${d.center_name}
        Date       : ${d.assigned_date}
        Time       : ${d.assigned_time_slot}

        Status     : ${d.status}
        ----------------------
        Please carry original documents.
    `;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Appointment_${d.request_id}.txt`;
    a.click();
    window.URL.revokeObjectURL(url);
}

// --- CITIZEN: TRACKING ---
async function trackRequest() {
    const id = document.getElementById('track_req_id').value;
    if (!id) return;

    try {
        const res = await fetch(`${API_BASE}/track_request?request_id=${id}`);
        const result = await res.json();

        const div = document.getElementById('trackResult');
        div.style.display = 'block';

        if (result.success) {
            const d = result.data;
            div.innerHTML = `
                <div style="display:flex; justify-content:space-between;">
                    <strong>${d.name}</strong>
                    <span class="badge ${d.status.includes('Confirmed') ? 'badge-success' : 'badge-warning'}">${d.status}</span>
                </div>
                <hr style="margin:5px 0;">
                <p style="font-size:0.9rem;">${d.assigned_date} @ ${d.assigned_time_slot}</p>
                <p style="font-size:0.8rem; color:#666;">Center ID: ${d.assigned_center_id}</p>
            `;
        } else {
            div.innerHTML = `<p style="color:red;">❌ Request Not Found</p>`;
        }
    } catch (err) { console.error(err); }
}

// --- ADMIN: DATA & CONTROLS ---
async function loadAdminData() {
    if (!currentUser) return;

    const ageGroup = document.getElementById('filter_age')?.value || 'All';
    const status = document.getElementById('filter_status')?.value || 'All';

    // Filter Payload
    const filter = {
        region: currentUser.region,
        age_group: ageGroup,
        status: status
    };

    try {
        const res = await fetch(`${API_BASE}/admin/data`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(filter)
        });
        const stats = await res.json();

        // Update Boxes
        document.getElementById('total_req').innerText = stats.total_req;
        document.getElementById('today_req').innerText = stats.today_req;
        document.getElementById('redirects').innerText = stats.overload_redirects;

        // Update Table
        const tbody = document.getElementById('logsTableBody');
        tbody.innerHTML = '';
        stats.logs.forEach(log => {
            const row = `<tr>
                <td><small>${log.request_id}</small></td>
                <td>${log.name || 'N/A'}</td>
                <td>${log.age_group || '-'}</td>
                <td>${log.assigned_center_id}</td>
                <td>${log.assigned_date} <small>${log.assigned_time_slot}</small></td>
                <td><span class="badge ${log.status.includes('Confirmed') ? 'badge-success' : 'badge-warning'}">${log.status}</span></td>
            </tr>`;
            tbody.innerHTML += row;
        });

    } catch (err) { console.error(err); }
}

async function loadCentersForAdmin() {
    try {
        const response = await fetch(`${API_BASE}/centers`);
        const centers = await response.json();
        const select = document.getElementById('centerSelect');
        if (select) {
            select.innerHTML = '';
            centers.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.center_id;
                opt.innerText = c.name;
                select.appendChild(opt);
            });
        }
    } catch (e) { }
}

async function triggerRedistribution() {
    const centerId = document.getElementById('centerSelect').value;
    const res = await fetch(`${API_BASE}/admin/redistribute`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ center_id: centerId })
    });
    const data = await res.json();
    showToast(data.message);
    loadAdminData();
}

function triggerNetworkFailure() {
    showToast("⚠️ Outage Alert Sent to All Centers");
}

async function resetSystem() {
    if (confirm("Confirm Full System Reset?")) {
        await fetch(`${API_BASE}/reset`, { method: 'POST' });
        loadAdminData();
        showToast("System Data Wiped");
    }
}

// --- UTILS ---
function showToast(msg) {
    const t = document.getElementById('toast');
    t.innerText = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3000);
}
