/* Utility and formatting helpers for VERDE */

export function formatMetric(val, decimals = 2) {
    if (val === null || val === undefined || isNaN(val)) {
        return `<span style="color: var(--text-light); font-weight: 500;">N/A</span>`;
    }
    return Number(val).toFixed(decimals);
}

export function formatBps(val) {
    if (val === null || val === undefined || isNaN(val)) {
        return `<span style="color: var(--text-light); font-weight: 500;">N/A</span>`;
    }
    return `${Number(val).toFixed(2)} bps`;
}

export function formatTimestamp(isoStr) {
    if (!isoStr) return "N/A";
    const d = new Date(isoStr);
    return d.toLocaleString();
}

export function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = "toast";
    
    let iconName = "info";
    if (type === "success") iconName = "check-circle";
    if (type === "error") iconName = "alert-circle";
    if (type === "warning") iconName = "alert-triangle";

    toast.innerHTML = `
        <i data-lucide="${iconName}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);
    if (window.lucide) window.lucide.createIcons();

    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

export function renderBadge(status, text) {
    let badgeClass = "badge-info";
    const s = String(status).toUpperCase();

    if (s.includes("PORTFOLIO_EMPTY") || s === "EMPTY") {
        badgeClass = "badge-warning";
    } else if (s.includes("PASS") || s.includes("SUCCESS") || s.includes("COMPLETE") || s.includes("VALID") || s.includes("CONNECTED")) {
        badgeClass = "badge-success";
    } else if (s.includes("REJECT") || s.includes("FAIL") || s.includes("ERROR") || s.includes("DISCONNECTED")) {
        badgeClass = "badge-danger";
    } else if (s.includes("WARN") || s.includes("NEAR_MISS") || s.includes("REGENERATE") || s.includes("RUNNING") || s.includes("SUBMITTED")) {
        badgeClass = "badge-warning";
    } else if (s.includes("PARETO")) {
        badgeClass = "badge-pareto";
    }

    return `<span class="badge ${badgeClass}">${text || status}</span>`;
}

export function updateUserUI(userInfo) {
    if (!userInfo) return;
    const email = typeof userInfo === 'string' ? userInfo : (userInfo.email || userInfo.username || 'Lead Quant');
    const namePart = email.includes('@') ? email.split('@')[0] : email;
    
    // Clean numbers and format
    const cleanName = namePart.replace(/[0-9]/g, '').trim() || namePart;
    const formattedName = cleanName.replace(/[._-]/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    
    // Initials (up to 2 chars)
    const words = formattedName.split(/\s+/).filter(Boolean);
    const initials = words.length >= 2 
        ? (words[0][0] + words[1][0]).toUpperCase()
        : namePart.slice(0, 2).toUpperCase();

    // Deterministic tag
    const hashNum = Math.abs(email.split('').reduce((a, b) => ((a << 5) - a) + b.charCodeAt(0), 0) % 9000 + 1000);
    const tag = `#${namePart.toLowerCase().slice(0, 4)}-${hashNum}`;

    const avatarEl = document.getElementById("sidebar-user-avatar");
    const nameEl = document.getElementById("sidebar-user-name");
    const tagEl = document.getElementById("sidebar-user-tag");
    const workspaceEl = document.getElementById("sidebar-workspace-title");
    const headerUserEl = document.getElementById("user-display");

    if (avatarEl) avatarEl.textContent = initials;
    if (nameEl) nameEl.textContent = formattedName;
    if (tagEl) tagEl.textContent = tag;
    if (workspaceEl) workspaceEl.textContent = `${formattedName.split(' ')[0]}'s Alpha Lab`;
    if (headerUserEl) headerUserEl.textContent = formattedName;

    // Persist in localStorage
    try {
        localStorage.setItem("verde_active_user", JSON.stringify({ email, formattedName, initials, tag }));
    } catch (e) {}
}

export function loadSavedUserUI() {
    try {
        const saved = localStorage.getItem("verde_active_user");
        if (saved) {
            updateUserUI(JSON.parse(saved));
        }
    } catch (e) {}
}

export async function syncBrainStatus() {
    try {
        const { api } = await import('./api.js');
        const health = await api.getBrainHealth();
        const brainDot = document.getElementById("brain-dot");
        const brainText = document.getElementById("brain-status-text");
        if (brainDot && brainText) {
            if (health && (health.connected || health.status === "ONLINE" || health.status === "CONNECTED")) {
                brainDot.className = "status-dot online";
                brainText.textContent = health.environment === "SIMULATION" ? "BRAIN: Sandbox" : "BRAIN: Connected";
            } else {
                brainDot.className = "status-dot offline";
                brainText.textContent = "BRAIN: Disconnected";
            }
        }
        if (health && health.email) {
            updateUserUI(health.email);
        }
        return health;
    } catch (e) {
        console.warn("Failed to sync brain status:", e);
    }
}

export function renderTabSkeleton(container) {
    if (!container) return;
    container.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px;">
            <div class="skeleton-box" style="height: 76px; border-radius: var(--radius-md);"></div>
            <div class="skeleton-box" style="height: 76px; border-radius: var(--radius-md);"></div>
            <div class="skeleton-box" style="height: 76px; border-radius: var(--radius-md);"></div>
            <div class="skeleton-box" style="height: 76px; border-radius: var(--radius-md);"></div>
        </div>

        <div class="skeleton-card">
            <div class="skeleton-header">
                <div class="skeleton-box skeleton-title-bar"></div>
                <div class="skeleton-box skeleton-btn"></div>
            </div>
            <div class="skeleton-box skeleton-table-header"></div>
            <div class="skeleton-row"><div class="skeleton-box skeleton-cell"></div><div class="skeleton-box skeleton-cell"></div><div class="skeleton-box skeleton-cell"></div></div>
            <div class="skeleton-row"><div class="skeleton-box skeleton-cell"></div><div class="skeleton-box skeleton-cell"></div><div class="skeleton-box skeleton-cell"></div></div>
            <div class="skeleton-row"><div class="skeleton-box skeleton-cell"></div><div class="skeleton-box skeleton-cell"></div><div class="skeleton-box skeleton-cell"></div></div>
            <div class="skeleton-row"><div class="skeleton-box skeleton-cell"></div><div class="skeleton-box skeleton-cell"></div><div class="skeleton-box skeleton-cell"></div></div>
        </div>
    `;
}
