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

    body.innerHTML = `<div style="text-align: center; padding: 40px; color: var(--text-muted);"><i data-lucide="loader" class="spin" style="width: 28px; height: 28px; margin-bottom: 10px; color: var(--status-warning);"></i><div>Loading diagnostic telemetry...</div></div>`;
    if (window.lucide) window.lucide.createIcons();

    try {
        const s = await api.getSimulationDetail(simulationId);
        const isTechFail = s.classification === "TECHNICAL_FAILURE" || s.portfolio_status === "EMPTY";

        body.innerHTML = `
            <!-- Top Summary Header -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; padding-bottom: 12px; border-bottom: 1px solid var(--border-color); flex-wrap: wrap; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-family: monospace; font-size: 13px; font-weight: 700; background: #f8fafc; border: 1px solid var(--border-color); padding: 3px 8px; border-radius: var(--radius-sm);">
                        SIM-${s.id.substring(0, 8)}
                    </span>
                    ${s.brain_sim_id ? `<span style="font-size: 12px; color: var(--text-muted);">BRAIN ID: <code>${s.brain_sim_id}</code></span>` : ''}
                </div>
                <div style="font-size: 12px; color: var(--text-muted);">
                    Submitted: ${formatTimestamp(s.submitted_at)}
                </div>
            </div>

            <!-- Diagnostic Alert Banner -->
            <div class="diagnostic-banner" style="background: ${isTechFail ? 'rgba(239, 68, 68, 0.08)' : 'rgba(234, 179, 8, 0.08)'}; border-left: 4px solid ${isTechFail ? 'var(--status-danger)' : 'var(--status-warning)'}; padding: 14px 16px; border-radius: var(--radius-sm); margin-bottom: 18px;">
                <div class="diagnostic-title" style="font-weight: 700; color: ${isTechFail ? 'var(--status-danger)' : '#ca8a04'}; font-size: 13px; display: flex; align-items: center; gap: 6px;">
                    <i data-lucide="${isTechFail ? 'alert-octagon' : 'alert-triangle'}" style="width: 16px; height: 16px;"></i>
                    Classification: ${s.classification} (Status: ${s.status})
                </div>
                <div class="diagnostic-detail" style="margin-top: 6px; font-size: 12.5px; line-height: 1.5; color: var(--text-main);">
                    ${s.diagnostic_reason || 'Simulation completed without active portfolio trades or valid Sharpe metrics.'}
                </div>
            </div>

            <!-- Expression Box -->
            <div style="margin-bottom: 16px;">
                <label style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.3px;">
                    Evaluated Alpha Formula
                </label>
                <div class="code-expr" style="display: block; width: 100%; font-size: 12.5px; padding: 10px 12px; margin-top: 4px; border-radius: var(--radius-sm); box-sizing: border-box;">
                    ${s.expression || 'N/A'}
                </div>
            </div>

            <!-- 4-Pill State Grid -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 16px;">
                <div style="padding: 10px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light); text-align: center;">
                    <div style="font-size: 10.5px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Remote Status</div>
                    <div style="margin-top: 4px;">${renderBadge(s.status)}</div>
                </div>
                <div style="padding: 10px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light); text-align: center;">
                    <div style="font-size: 10.5px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Classification</div>
                    <div style="margin-top: 4px;">${renderBadge(s.classification)}</div>
                </div>
                <div style="padding: 10px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light); text-align: center;">
                    <div style="font-size: 10.5px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Portfolio State</div>
                    <div style="margin-top: 4px;">${renderBadge(s.portfolio_status)}</div>
                </div>
                <div style="padding: 10px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-light); text-align: center;">
                    <div style="font-size: 10.5px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Metrics State</div>
                    <div style="margin-top: 4px;">${renderBadge(s.metrics_status)}</div>
                </div>
            </div>

            <!-- Root Cause & Settings Grid -->
            <div class="card" style="margin: 0 0 16px 0; padding: 14px; background: #ffffff;">
                <div style="font-size: 12.5px; margin-bottom: 8px;">
                    <strong style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">Identified Root Cause:</strong>
                    <p style="margin-top: 4px; color: var(--text-main); font-size: 12.5px; line-height: 1.4;">
                        ${s.possible_cause || 'Signal evaluated to constant, zero, or un-cross-sectionally differentiable values across all target instruments.'}
                    </p>
                </div>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; font-size: 12px; margin-top: 10px; padding-top: 8px; border-top: 1px solid var(--border-light);">
                    <div><span style="color: var(--text-muted);">Universe:</span> <strong>${s.universe || 'TOP3000'}</strong></div>
                    <div><span style="color: var(--text-muted);">Region:</span> <strong>${s.region || 'USA'}</strong></div>
                    <div><span style="color: var(--text-muted);">Delay:</span> <strong>${s.delay ?? 1}</strong></div>
                    <div><span style="color: var(--text-muted);">Neutralization:</span> <strong>${s.neutralization || 'SUBINDUSTRY'}</strong></div>
                </div>
            </div>

            <!-- Raw Response Viewer (Collapsible) -->
            ${s.raw_response ? `
                <div style="margin-bottom: 18px;">
                    <details style="background: #0f172a; border-radius: var(--radius-sm); padding: 10px; color: #cbd5e1; font-size: 11.5px;">
                        <summary style="cursor: pointer; font-weight: 600; color: #94a3b8; user-select: none;">
                            <i data-lucide="code" style="width: 12px; height: 12px; display: inline;"></i> View Raw API Response Telemetry
                        </summary>
                        <pre style="margin-top: 8px; max-height: 140px; overflow-y: auto; font-family: monospace; white-space: pre-wrap; word-break: break-all; color: #a5f3fc;">${JSON.stringify(s.raw_response, null, 2)}</pre>
                    </details>
                </div>
            ` : ''}

            <!-- Footer Action Buttons -->
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; padding-top: 10px; border-top: 1px solid var(--border-color);">
                <button class="btn btn-outline btn-sm" onclick="window.verdeUI.closeDiagnosticModal(); window.verdeUI.openCandidateModal('${s.candidate_id}')">
                    <i data-lucide="microscope" style="width: 13px; height: 13px;"></i> Inspect Candidate
                </button>
                <div style="display: flex; gap: 8px;">
                    <button class="btn btn-outline btn-sm" onclick="window.verdeUI.closeDiagnosticModal()">
                        Close
                    </button>
                    <button class="btn btn-primary btn-sm" onclick="window.verdeUI.pollSimulation('${s.id}')">
                        <i data-lucide="refresh-cw" style="width: 13px; height: 13px;"></i> Re-Poll BRAIN
                    </button>
                </div>
            </div>
        `;

        if (window.lucide) window.lucide.createIcons();
    } catch (err) {
        body.innerHTML = `<div class="card" style="color: var(--status-danger);">Error loading diagnostics: ${err.message}</div>`;
    }
}
