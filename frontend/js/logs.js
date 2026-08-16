import { api } from './api.js';
import { formatTimestamp, renderBadge } from './utils.js';

export async function renderLogs(container) {
    container.innerHTML = `<div style="text-align: center; padding: 40px;"><i data-lucide="loader" class="spin"></i> Loading Structured Logs...</div>`;
    if (window.lucide) window.lucide.createIcons();

    try {
        const logs = await api.getLogs({ limit: 100 });

        let rows = logs.map(l => `
            <tr>
                <td><span style="font-size: 11px; color: var(--text-muted);">${formatTimestamp(l.timestamp)}</span></td>
                <td>${renderBadge(l.severity)}</td>
                <td><span class="badge badge-info">${l.component}</span></td>
                <td><strong>${l.event}</strong></td>
                <td>${l.message}</td>
                <td style="white-space: nowrap;">
                    <button class="btn-action-icon" onclick="window.verdeUI.openLogDetailModal('${l.id}')" title="Inspect Log Entry">
                        <i data-lucide="info"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div>
                        <h3 class="card-title"><i data-lucide="terminal"></i> System & Research Audit Logs</h3>
                        <span class="card-subtitle">Structured, secret-redacted event stream across preflight, simulations, and background workers</span>
                    </div>
                    <button class="btn btn-outline btn-sm" onclick="window.verdeUI.navigateTo('logs')">
                        <i data-lucide="refresh-cw"></i> Refresh
                    </button>
                </div>

                ${logs.length > 0 ? `
                    <div class="table-container">
                        <table class="verde-table">
                            <thead>
                                <tr>
                                    <th>Timestamp</th>
                                    <th>Severity</th>
                                    <th>Component</th>
                                    <th>Event</th>
                                    <th>Message</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rows}
                            </tbody>
                        </table>
                    </div>
                ` : `
                    <div style="text-align: center; padding: 40px; color: var(--text-muted);">
                        No log entries found.
                    </div>
                `}
            </div>
        `;

        if (window.lucide) window.lucide.createIcons();
    } catch (err) {
        container.innerHTML = `<div class="card" style="color: var(--status-danger);">Error: ${err.message}</div>`;
    }
}

export async function populateDiagnosticModal(simulationId) {
    const body = document.getElementById("diagnostic-modal-body");
    if (!body) return;

    body.innerHTML = `<div style="text-align: center; padding: 20px;"><i data-lucide="loader" class="spin"></i> Loading diagnostic record...</div>`;
    if (window.lucide) window.lucide.createIcons();

    try {
        const s = await api.getSimulationDetail(simulationId);

        body.innerHTML = `
            <div class="diagnostic-banner">
                <div class="diagnostic-title">Event: SIMULATION_${s.status}</div>
                <div class="diagnostic-detail">
                    ${s.diagnostic_reason || 'BRAIN completed the simulation but returned no usable portfolio metrics.'}
                </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 12px; font-size: 13px; margin-bottom: 16px;">
                <div><strong>Alpha Expression:</strong> <div class="code-expr" style="display: block; margin-top: 4px;">${s.expression || 'N/A'}</div></div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                    <div><strong>Remote BRAIN Status:</strong> ${renderBadge(s.status)}</div>
                    <div><strong>Classification:</strong> ${renderBadge(s.classification)}</div>
                    <div><strong>Portfolio Status:</strong> ${renderBadge(s.portfolio_status)}</div>
                    <div><strong>Metrics Status:</strong> ${renderBadge(s.metrics_status)}</div>
                </div>
                <div><strong>Possible Cause:</strong> ${s.possible_cause || 'Signal may have evaluated to constant or near-constant values across the universe.'}</div>
                <div><strong>Submitted At:</strong> ${formatTimestamp(s.submitted_at)}</div>
            </div>

            <div style="text-align: right;">
                <button class="btn btn-outline btn-sm" onclick="window.verdeUI.closeDiagnosticModal()">Close</button>
            </div>
        `;

        if (window.lucide) window.lucide.createIcons();
    } catch (err) {
        body.innerHTML = `<div style="color: var(--status-danger);">Error: ${err.message}</div>`;
    }
}
