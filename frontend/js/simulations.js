import { api } from './api.js';
import { formatBps, formatMetric, formatTimestamp, renderBadge, showToast } from './utils.js';

export async function renderSimulations(container) {
    container.innerHTML = `<div style="text-align: center; padding: 40px;"><i data-lucide="loader" class="spin"></i> Loading Simulations...</div>`;
    if (window.lucide) window.lucide.createIcons();

    try {
        const sims = await api.getSimulations({ limit: 100 });

        let tableRows = sims.map(s => {
            const isTechFail = s.classification === "TECHNICAL_FAILURE" || s.portfolio_status === "EMPTY";
            return `
                <tr>
                    <td><span style="font-family: monospace; font-size: 11px; color: var(--text-muted);">${s.id.substring(0, 8)}</span></td>
                    <td><div class="code-expr">${s.expression || 'N/A'}</div></td>
                    <td><span class="badge badge-info">${s.family_code || 'OTHER'}</span></td>
                    <td>${renderBadge(s.status)}</td>
                    <td>${renderBadge(s.portfolio_status)}</td>
                    <td>${renderBadge(s.metrics_status)}</td>
                    <td><strong>${formatMetric(s.sharpe)}</strong></td>
                    <td><strong>${formatMetric(s.fitness)}</strong></td>
                    <td>${formatMetric(s.turnover)}</td>
                    <td>${formatBps(s.margin_bps)}</td>
                    <td style="white-space: nowrap;">
                        <div class="table-action-group">
                            ${isTechFail ? `
                                <button class="btn-action-diag" onclick="window.verdeUI.openDiagnosticModal('${s.id}')" title="Inspect Diagnostic Reason">
                                    <i data-lucide="alert-triangle"></i>
                                    <span>Diagnostics</span>
                                </button>
                            ` : ''}
                            <button class="btn-action-icon" onclick="window.verdeUI.openCandidateModal('${s.candidate_id}')" title="Inspect Candidate">
                                <i data-lucide="eye"></i>
                            </button>
                            <button class="btn-action-icon" onclick="window.verdeUI.pollSimulation('${s.id}')" title="Poll Remote Status">
                                <i data-lucide="refresh-cw"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div>
                        <h3 class="card-title"><i data-lucide="play-circle"></i> WorldQuant BRAIN Simulation Monitor</h3>
                        <span class="card-subtitle">Explicit state machine separating technical failures from true alpha fitness</span>
                    </div>
                    <button class="btn btn-outline btn-sm" onclick="window.verdeUI.navigateTo('simulations')">
                        <i data-lucide="refresh-cw"></i> Refresh Table
                    </button>
                </div>

                ${sims.length > 0 ? `
                    <div class="table-container">
                        <table class="verde-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Alpha Expression</th>
                                    <th>Family</th>
                                    <th>Sim Status</th>
                                    <th>Portfolio</th>
                                    <th>Metrics</th>
                                    <th>Sharpe</th>
                                    <th>Fitness</th>
                                    <th>Turnover</th>
                                    <th>Margin</th>
                                    <th>Diagnostics & Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${tableRows}
                            </tbody>
                        </table>
                    </div>
                ` : `
                    <div style="text-align: center; padding: 40px; color: var(--text-muted);">
                        <i data-lucide="inbox" style="width: 32px; height: 32px; margin-bottom: 8px;"></i>
                        <p>No simulations submitted yet. Launch Alpha Lab to generate and submit candidates.</p>
                    </div>
                `}
            </div>
        `;

        if (window.lucide) window.lucide.createIcons();

        // If any simulation is running/submitting, auto-refresh after 2.5s
        const hasRunning = sims.some(s => s.status === 'RUNNING' || s.status === 'SUBMITTING');
        if (hasRunning) {
            setTimeout(() => {
                const curPage = window.location.hash.replace('#', '') || 'dashboard';
                if (curPage === 'simulations') {
                    renderSimulations(container);
                }
            }, 2500);
        }
    } catch (err) {
        container.innerHTML = `<div class="card" style="color: var(--status-danger);">Error: ${err.message}</div>`;
    }
}
