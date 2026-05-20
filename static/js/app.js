/* ==========================================================================
   AETHER SHIELD - SECURE AUTH LAB JS LAYER
   ========================================================================== */

// Global State
let CURRENT_SESSION = null;
let LOCKOUT_INTERVAL = null;

// On Page Load
document.addEventListener("DOMContentLoaded", () => {
    checkActiveSession();
    loadLiveDatabase();
    loadActiveSessions();
    runTimingAttack(); // Run once to seed the timing simulator
});

// --- TOAST NOTIFICATIONS ---

function showToast(message, type = "success") {
    const toast = document.getElementById("toast-message");
    const toastText = document.getElementById("toast-text");
    
    toast.className = `toast ${type}`;
    toastText.innerText = message;
    
    // Slide in
    toast.classList.remove("hidden");
    
    // Automatically dismiss after 4 seconds
    setTimeout(() => {
        toast.classList.add("hidden");
    }, 4000);
}

// --- PASSWORD STRENGTH METER ---

function checkPasswordStrength() {
    const pwdInput = document.getElementById("reg-password");
    const meter = document.querySelector(".strength-meter");
    const text = document.getElementById("strength-text");
    const password = pwdInput.value;
    
    if (password.length === 0) {
        meter.className = "strength-meter";
        text.innerText = "Too short";
        return;
    }
    
    if (password.length < 8) {
        meter.className = "strength-meter weak";
        text.innerText = "Too short (min 8)";
        return;
    }
    
    let strength = 0;
    if (/[a-z]/.test(password)) strength++; // lowercase
    if (/[A-Z]/.test(password)) strength++; // uppercase
    if (/[0-9]/.test(password)) strength++; // digit
    if (/[^A-Za-z0-9]/.test(password)) strength++; // special char
    
    if (strength <= 2) {
        meter.className = "strength-meter weak";
        text.innerText = "Weak";
    } else if (strength === 3) {
        meter.className = "strength-meter medium";
        text.innerText = "Medium";
    } else {
        meter.className = "strength-meter strong";
        text.innerText = "Strong Security!";
    }
}

// --- VIEW UTILITIES ---

function switchAuthTab(tab) {
    const loginBtn = document.getElementById("tab-login-btn");
    const regBtn = document.getElementById("tab-register-btn");
    const loginForm = document.getElementById("login-form-container");
    const regForm = document.getElementById("register-form-container");
    
    if (tab === "login") {
        loginBtn.classList.add("active");
        regBtn.classList.remove("active");
        loginForm.classList.remove("hidden");
        regForm.classList.add("hidden");
    } else {
        loginBtn.classList.remove("active");
        regBtn.classList.add("active");
        loginForm.classList.add("hidden");
        regForm.classList.remove("hidden");
    }
}

function switchSandboxTab(tab) {
    // Buttons
    const tabs = document.querySelectorAll(".sandbox-tab");
    tabs.forEach(btn => btn.classList.remove("active"));
    
    // Panels
    const panels = document.querySelectorAll(".sandbox-panel");
    panels.forEach(p => p.classList.add("hidden"));
    
    if (tab === "db") {
        tabs[0].classList.add("active");
        document.getElementById("sandbox-db-panel").classList.remove("hidden");
        loadLiveDatabase();
    } else if (tab === "sessions") {
        tabs[1].classList.add("active");
        document.getElementById("sandbox-sessions-panel").classList.remove("hidden");
        loadActiveSessions();
    } else if (tab === "timing") {
        tabs[2].classList.add("active");
        document.getElementById("sandbox-timing-panel").classList.remove("hidden");
    }
}

function switchAdminTab(tab) {
    const tabs = document.querySelectorAll(".admin-tab");
    tabs.forEach(btn => btn.classList.remove("active"));
    
    const panels = document.querySelectorAll(".admin-panel");
    panels.forEach(p => p.classList.add("hidden"));
    
    if (tab === "users") {
        tabs[0].classList.add("active");
        document.getElementById("admin-users-panel").classList.remove("hidden");
        loadAdminUsersTable();
    } else {
        tabs[1].classList.add("active");
        document.getElementById("admin-logs-panel").classList.remove("hidden");
        loadAdminLogs();
    }
}

function togglePasswordVisibility(inputId, icon) {
    const input = document.getElementById(inputId);
    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    } else {
        input.type = "password";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    }
}

// --- PASSWORD RESET MODAL SYSTEM ---

function openResetModal() {
    document.getElementById("reset-modal").classList.remove("hidden");
    document.getElementById("reset-step-1").classList.remove("hidden");
    document.getElementById("reset-step-2").classList.add("hidden");
    document.getElementById("reset-username").value = "";
    document.getElementById("reset-answer").value = "";
    document.getElementById("reset-new-password").value = "";
}

function closeResetModal() {
    document.getElementById("reset-modal").classList.add("hidden");
}

// --- API ACTIONS: ACCOUNT MANAGEMENT & AUTH ---

async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById("reg-username").value;
    const role = document.getElementById("reg-role").value;
    const password = document.getElementById("reg-password").value;
    const question = document.getElementById("reg-question").value;
    const answer = document.getElementById("reg-answer").value;
    const algo = document.getElementById("reg-algo").value;
    
    if (!question) {
        showToast("Please select a security question.", "error");
        return;
    }
    
    try {
        const response = await fetch("/api/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: username,
                password: password,
                role: role,
                security_question: question,
                security_answer: answer,
                hash_algo: algo
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(data.message || "User registered successfully!", "success");
            // Clear form
            document.getElementById("register-form").reset();
            // Go to login tab
            switchAuthTab("login");
            // Reload inspector DB
            loadLiveDatabase();
        } else {
            showToast(data.error || "Registration failed.", "error");
        }
    } catch (err) {
        showToast("Connection error. Could not connect to server.", "error");
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const usernameInput = document.getElementById("login-username");
    const passwordInput = document.getElementById("login-password");
    const submitBtn = document.getElementById("login-submit-btn");
    
    const username = usernameInput.value;
    const password = passwordInput.value;
    
    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(data.message || "Welcome back!", "success");
            
            // Save details to LocalStorage
            localStorage.setItem("session_token", data.token);
            localStorage.setItem("user_role", data.role);
            localStorage.setItem("username", data.username);
            
            passwordInput.value = ""; // Clear password
            
            // Set session state and switch view
            CURRENT_SESSION = {
                token: data.token,
                role: data.role,
                username: data.username
            };
            
            renderLoggedInState();
            loadLiveDatabase();
            loadActiveSessions();
        } else {
            showToast(data.error || "Login failed.", "error");
            
            // If locked out, check if response indicates account locked out
            if (data.error && data.error.includes("Account is locked")) {
                // Parse seconds
                const matches = data.error.match(/\d+/);
                if (matches) {
                    startLockoutCountdown(parseInt(matches[0]), submitBtn);
                }
            } else if (data.error && data.error.includes("locked for 30 seconds")) {
                startLockoutCountdown(30, submitBtn);
            }
        }
    } catch (err) {
        showToast("Connection error. Could not connect to server.", "error");
    }
}

function startLockoutCountdown(seconds, buttonElement) {
    clearInterval(LOCKOUT_INTERVAL);
    let remaining = seconds;
    
    buttonElement.disabled = true;
    buttonElement.style.opacity = "0.5";
    
    LOCKOUT_INTERVAL = setInterval(() => {
        remaining--;
        buttonElement.querySelector("span").innerText = `LOCKED (${remaining}s)`;
        
        if (remaining <= 0) {
            clearInterval(LOCKOUT_INTERVAL);
            buttonElement.disabled = false;
            buttonElement.style.opacity = "1";
            buttonElement.querySelector("span").innerText = "SIGN IN";
            showToast("Account lockout has expired. You can try again.", "success");
            loadLiveDatabase(); // Reload live db to show unlock
        }
    }, 1000);
}

async function handleLogout() {
    const token = localStorage.getItem("session_token");
    
    try {
        await fetch("/api/logout", {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` }
        });
    } catch (err) {
        console.error("Logout request failed, cleaning local state anyway");
    }
    
    // Clean local storage regardless
    localStorage.removeItem("session_token");
    localStorage.removeItem("user_role");
    localStorage.removeItem("username");
    
    CURRENT_SESSION = null;
    
    // Update view
    document.getElementById("logged-in-view").classList.add("hidden");
    document.getElementById("logged-out-view").classList.remove("hidden");
    
    showToast("Logged out successfully.", "success");
    loadLiveDatabase();
    loadActiveSessions();
}

function checkActiveSession() {
    const token = localStorage.getItem("session_token");
    const role = localStorage.getItem("user_role");
    const username = localStorage.getItem("username");
    
    if (token && role && username) {
        CURRENT_SESSION = { token, role, username };
        renderLoggedInState();
    }
}

function renderLoggedInState() {
    if (!CURRENT_SESSION) return;
    
    document.getElementById("logged-out-view").classList.add("hidden");
    document.getElementById("logged-in-view").classList.remove("hidden");
    
    // Header welcome
    document.getElementById("dash-username").innerText = CURRENT_SESSION.username;
    
    // Badge
    const roleBadge = document.getElementById("dash-role-badge");
    roleBadge.innerText = CURRENT_SESSION.role.toUpperCase();
    
    if (CURRENT_SESSION.role === "admin") {
        roleBadge.className = "badge admin-badge";
        roleBadge.style.borderColor = "var(--accent-purple)";
        roleBadge.style.color = "var(--accent-purple)";
        roleBadge.style.background = "rgba(168, 85, 247, 0.15)";
        
        // Show Admin panel, hide standard user
        document.getElementById("user-dashboard-view").classList.add("hidden");
        document.getElementById("admin-dashboard-view").classList.remove("hidden");
        
        // Seed first sub-tab
        switchAdminTab("users");
    } else {
        roleBadge.className = "badge user-badge";
        roleBadge.style.borderColor = "var(--accent-indigo)";
        roleBadge.style.color = "var(--accent-indigo)";
        roleBadge.style.background = "rgba(99, 102, 241, 0.15)";
        
        // Show standard user, hide admin
        document.getElementById("user-dashboard-view").classList.remove("hidden");
        document.getElementById("admin-dashboard-view").classList.add("hidden");
        
        // Profile items
        document.getElementById("user-token-value").innerText = CURRENT_SESSION.token;
        document.getElementById("user-role-value").innerText = "Standard Authorized User";
    }
}

// --- PASSWORD RESET API CALLS ---

async function requestSecurityQuestion() {
    const username = document.getElementById("reset-username").value;
    if (!username) {
        showToast("Please enter a username first.", "error");
        return;
    }
    
    try {
        const response = await fetch("/api/reset-request", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById("reset-question-text").innerText = data.security_question;
            document.getElementById("reset-step-1").classList.add("hidden");
            document.getElementById("reset-step-2").classList.remove("hidden");
        } else {
            showToast(data.error || "Username not found.", "error");
        }
    } catch (err) {
        showToast("Server error. Try again later.", "error");
    }
}

async function confirmPasswordReset() {
    const username = document.getElementById("reset-username").value;
    const answer = document.getElementById("reset-answer").value;
    const newPwd = document.getElementById("reset-new-password").value;
    
    if (!answer || !newPwd) {
        showToast("Please fill in all reset fields.", "error");
        return;
    }
    
    try {
        const response = await fetch("/api/reset-confirm", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: username,
                security_answer: answer,
                new_password: newPwd
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(data.message || "Password changed!", "success");
            closeResetModal();
            loadLiveDatabase();
        } else {
            showToast(data.error || "Reset failed.", "error");
            
            // Lock check in reset flow as well
            if (data.error && data.error.includes("Account locked")) {
                closeResetModal();
            }
        }
    } catch (err) {
        showToast("Connection failed during reset.", "error");
    }
}

// --- ADMIN CONTROLS (RBAC) ---

async function loadAdminUsersTable() {
    const token = localStorage.getItem("session_token");
    const tbody = document.getElementById("admin-users-table-body");
    tbody.innerHTML = `<tr><td colspan="6" style="text-align: center;">Retrieving user entries...</td></tr>`;
    
    try {
        const response = await fetch("/api/admin/users", {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (!response.ok) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--accent-red)">Failed to load directory. Unauthorized access.</td></tr>`;
            return;
        }
        
        const users = await response.json();
        tbody.innerHTML = "";
        
        users.forEach(user => {
            const tr = document.createElement("tr");
            
            // Check lockout state
            let lockStatus = `<span style="color: var(--accent-green); font-weight: bold;"><i class="fa-solid fa-lock-open"></i> Active</span>`;
            let unlockBtn = "";
            
            if (user.lockout_until) {
                const lockoutTime = new Date(user.lockout_until);
                const now = new Date();
                if (now < lockoutTime) {
                    lockStatus = `<span style="color: var(--accent-red); font-weight: bold;"><i class="fa-solid fa-lock"></i> Locked</span>`;
                    unlockBtn = `<button class="action-btn-small" onclick="adminUnlockUser('${user.username}')"><i class="fa-solid fa-key"></i> Unlock</button>`;
                }
            }
            
            // Role toggling representation
            const roleActionText = user.role === "admin" ? "Demote" : "Promote";
            const roleActionVal = user.role === "admin" ? "user" : "admin";
            
            tr.innerHTML = `
                <td class="td-username">${user.username}</td>
                <td><span class="badge ${user.role}-badge" style="${user.role === 'admin' ? 'border-color: var(--accent-purple); color: var(--accent-purple); background: rgba(168, 85, 247, 0.15)' : ''}">${user.role.toUpperCase()}</span></td>
                <td style="font-family: var(--font-mono); font-size: 0.75rem;">${user.hash_algo}</td>
                <td style="text-align: center; font-weight: bold;">${user.failed_attempts}</td>
                <td>${lockStatus}</td>
                <td>
                    <div class="action-row-btns">
                        ${unlockBtn}
                        <button class="action-btn-small" onclick="adminChangeRole('${user.username}', '${roleActionVal}')">${roleActionText}</button>
                        <button class="action-btn-small danger" onclick="adminDeleteUser('${user.username}')"><i class="fa-solid fa-trash"></i></button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--accent-red)">Connection error loading users.</td></tr>`;
    }
}

async function adminUnlockUser(targetUser) {
    const token = localStorage.getItem("session_token");
    try {
        const response = await fetch("/api/admin/unlock", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ username: targetUser })
        });
        
        const data = await response.json();
        if (response.ok) {
            showToast(data.message, "success");
            loadAdminUsersTable();
            loadLiveDatabase();
        } else {
            showToast(data.error, "error");
        }
    } catch (err) {
        showToast("Unlock request failed.", "error");
    }
}

async function adminChangeRole(targetUser, newRole) {
    const token = localStorage.getItem("session_token");
    try {
        const response = await fetch("/api/admin/change-role", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ username: targetUser, role: newRole })
        });
        
        const data = await response.json();
        if (response.ok) {
            showToast(data.message, "success");
            
            // If admin demoted themselves, trigger reload/logout logic as role changed!
            if (targetUser === CURRENT_SESSION.username) {
                CURRENT_SESSION.role = newRole;
                localStorage.setItem("user_role", newRole);
                renderLoggedInState();
            } else {
                loadAdminUsersTable();
            }
            loadLiveDatabase();
        } else {
            showToast(data.error, "error");
        }
    } catch (err) {
        showToast("Role change failed.", "error");
    }
}

async function adminDeleteUser(targetUser) {
    if (!confirm(`Are you absolutely sure you want to delete user '${targetUser}'?`)) return;
    
    const token = localStorage.getItem("session_token");
    try {
        const response = await fetch("/api/admin/delete", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ username: targetUser })
        });
        
        const data = await response.json();
        if (response.ok) {
            showToast(data.message, "success");
            loadAdminUsersTable();
            loadLiveDatabase();
        } else {
            showToast(data.error, "error");
        }
    } catch (err) {
        showToast("Delete failed.", "error");
    }
}

async function loadAdminLogs() {
    const token = localStorage.getItem("session_token");
    const container = document.getElementById("admin-logs-list");
    container.innerHTML = `<div style="text-align: center; padding: 1rem; color: var(--text-secondary);">Reading audit log file...</div>`;
    
    try {
        const response = await fetch("/api/admin/logs", {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (!response.ok) {
            container.innerHTML = `<div style="color: var(--accent-red); text-align: center; padding: 1rem;">Failed to retrieve logs. Unauthorized access.</div>`;
            return;
        }
        
        const logs = await response.json();
        container.innerHTML = "";
        
        if (logs.length === 0) {
            container.innerHTML = `<div style="text-align: center; padding: 1rem; color: var(--text-muted)">Audit logs empty.</div>`;
            return;
        }
        
        logs.forEach(log => {
            const timeStr = new Date(log.timestamp).toLocaleTimeString();
            const div = document.createElement("div");
            div.className = `log-row ${log.status}`;
            
            div.innerHTML = `
                <div class="log-meta">
                    <span class="log-type">${log.event_type} (${log.status})</span>
                    <span>${timeStr}</span>
                </div>
                <div class="log-desc">User: <strong>${log.username}</strong></div>
                <div class="log-details">${log.details || ''}</div>
            `;
            container.appendChild(div);
        });
    } catch (err) {
        container.innerHTML = `<div style="color: var(--accent-red); padding: 1rem;">Connection error loading audit trail.</div>`;
    }
}

// --- SANDBOX DEVELOPER PANELS ---

async function loadLiveDatabase() {
    const dbBlock = document.getElementById("db-json-block");
    try {
        const response = await fetch("/api/inspect-db");
        if (!response.ok) {
            dbBlock.innerText = "Error inspecting users.json file.";
            return;
        }
        
        const users = await response.json();
        
        // Remove security parameters to keep display clean but informative
        const displayUsers = JSON.parse(JSON.stringify(users)); // deep clone
        
        // Format beautiful JSON
        dbBlock.innerHTML = formatJsonHighlight(displayUsers);
    } catch (err) {
        dbBlock.innerText = "Could not reach database inspection node.";
    }
}

async function loadActiveSessions() {
    const sessionBlock = document.getElementById("sessions-json-block");
    try {
        const response = await fetch("/api/inspect-sessions");
        if (!response.ok) {
            sessionBlock.innerText = "Error inspecting session storage.";
            return;
        }
        
        const sessions = await response.json();
        sessionBlock.innerHTML = formatJsonHighlight(sessions);
    } catch (err) {
        sessionBlock.innerText = "Session inspection unreachable.";
    }
}

// Simple JSON highlighting formatter for high-end feel
function formatJsonHighlight(obj) {
    const jsonStr = JSON.stringify(obj, null, 4);
    
    // Safe escaping
    let escaped = jsonStr
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
        
    // Apply styling regexes
    return escaped.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)/g, function (match) {
        let cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
                // Highlight salts and hashes specifically in different cyber colors!
                if (match.length > 25) {
                    cls = 'crypto-string';
                }
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        
        // Return styled elements
        if (cls === 'key') {
            return `<span style="color: var(--accent-cyan); font-weight: bold;">${match}</span>`;
        } else if (cls === 'string') {
            return `<span style="color: #a5d6ff;">${match}</span>`;
        } else if (cls === 'crypto-string') {
            return `<span style="color: var(--accent-purple); font-family: var(--font-mono); font-size: 0.75rem;">${match}</span>`;
        } else if (cls === 'number') {
            return `<span style="color: var(--accent-green); font-weight: 500;">${match}</span>`;
        } else if (cls === 'boolean') {
            return `<span style="color: var(--accent-indigo); font-weight: bold;">${match}</span>`;
        } else {
            return `<span style="color: var(--text-muted);">${match}</span>`;
        }
    });
}

// --- TIMING ATTACK SIMULATOR CODE ---

async function runTimingAttack() {
    const candidateInput = document.getElementById("timing-candidate");
    const candidate = candidateInput.value;
    
    const earlyBar = document.getElementById("early-exit-bar");
    const earlyTimeText = document.getElementById("early-exit-time");
    
    const constBar = document.getElementById("constant-bar");
    const constTimeText = document.getElementById("constant-time");
    
    const verdict = document.getElementById("timing-verdict");
    
    try {
        const response = await fetch("/api/simulate-timing", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ candidate })
        });
        
        if (!response.ok) return;
        
        const data = await response.json();
        
        // Show times
        earlyTimeText.innerText = `${data.early_exit_us.toFixed(1)} us`;
        constTimeText.innerText = `${data.constant_time_us.toFixed(1)} us`;
        
        // We calculate width relative to a fixed scale of e.g. 50,000 microseconds to prevent chaotic jumping,
        // or a dynamic scale with a minimum ceiling.
        const maxTimeScale = Math.max(data.early_exit_us, data.constant_time_us, 100);
        
        const earlyPct = (data.early_exit_us / maxTimeScale) * 100;
        const constPct = (data.constant_time_us / maxTimeScale) * 100;
        
        earlyBar.style.width = `${earlyPct}%`;
        constBar.style.width = `${constPct}%`;
        
        // Update the educational description based on character matching length!
        const matchLen = data.matching_prefix_length;
        const candLen = data.candidate_length;
        
        if (matchLen > 0) {
            let matches = "secure_token_secret_xyz".substring(0, matchLen);
            verdict.innerHTML = `
                <div class="info-alert" style="color: var(--accent-red); background: rgba(244, 63, 94, 0.05); border: 1px solid rgba(244, 63, 94, 0.2)">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                    <span><strong>Timing Leakage!</strong> Prefix matches <strong>"${matches}"</strong> (${matchLen} chars). Early-exit comparison exits at char index ${matchLen}. An attacker measuring server response time can guess characters sequentially by looking for minor spikes in time! <strong>Constant-time operator remains immune.</strong></span>
                </div>
            `;
        } else {
            verdict.innerHTML = `
                <div class="info-alert">
                    <i class="fa-solid fa-brain"></i>
                    <span>Type characters matching the secret (starts with "s") to see how standard character comparisons expose matching characters by shifting early-exit speeds, while <code>secrets.compare_digest</code> stays flat.</span>
                </div>
            `;
        }
    } catch (err) {
        console.error("Timing attack request failed", err);
    }
}
