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

    if (s.includes("PASS") || s.includes("SUCCESS") || s.includes("COMPLETE") || s.includes("VALID") || s.includes("CONNECTED")) {
        badgeClass = "badge-success";
    } else if (s.includes("REJECT") || s.includes("FAIL") || s.includes("ERROR") || s.includes("EMPTY") || s.includes("DISCONNECTED")) {
        badgeClass = "badge-danger";
    } else if (s.includes("WARN") || s.includes("NEAR_MISS") || s.includes("REGENERATE") || s.includes("RUNNING") || s.includes("SUBMITTED")) {
        badgeClass = "badge-warning";
    } else if (s.includes("PARETO")) {
        badgeClass = "badge-pareto";
    }

    return `<span class="badge ${badgeClass}">${text || status}</span>`;
}
