import { api } from './api.js';
import { formatBps, formatMetric, formatTimestamp, renderBadge, showToast } from './utils.js';

export async function renderCandidates(container) {
    container.innerHTML = `<div style="text-align: center; padding: 40px;"><i data-lucide="loader" class="spin"></i> Loading Candidates...</div>`;
    if (window.lucide) window.lucide.createIcons();

    try {
        const candidates = await api.getCandidates({ limit: 100 });

        let rows = candidates.map(c => `
            <tr>
                <td><span style="font-family: monospace; font-size: 11px; color: var(--text-muted);">${c.id.substring(0, 8)}</span></td>
                <td><div class="code-expr">${c.expression}</div></td>
                <td><span class="badge badge-info">${c.family_code}</span></td>
                <td>${renderBadge(c.tier)}</td>
                <td>${renderBadge(c.preflight_status)}</td>
                <td>${c.is_pareto ? '<span class="badge badge-pareto">PARETO</span>' : '<span style="color: var(--text-light);">-</span>'}</td>
                <td><strong>${formatMetric(c.sharpe)}</strong></td>
                <td><strong>${formatMetric(c.fitness)}</strong></td>
                <td>${formatMetric(c.turnover)}</td>
                <td>${formatBps(c.margin_bps)}</td>
                <td style="white-space: nowrap;">
                    <div class="table-action-group">
                        <button class="btn-action-icon" onclick="window.verdeUI.openCandidateModal('${c.id}')" title="Inspect Candidate">
                            <i data-lucide="eye"></i>
                        </button>
                        ${c.preflight_status === 'PASS' ? `
                            <button class="btn-action-primary" onclick="window.verdeUI.simulateCandidate('${c.id}')" title="Submit to BRAIN">
                                <i data-lucide="play"></i>
                                <span>Simulate</span>
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `).join('');

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div>
                        <h3 class="card-title"><i data-lucide="file-code"></i> Alpha Candidate Repository</h3>
                        <span class="card-subtitle">Repository of all generated, preflighted, and simulated expressions</span>
                    </div>
                    <button class="btn btn-outline btn-sm" onclick="window.verdeUI.navigateTo('candidates')">
                        <i data-lucide="refresh-cw"></i> Refresh
                    </button>
                </div>

                ${candidates.length > 0 ? `
                    <div class="table-container">
                        <table class="verde-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Alpha Expression</th>
                                    <th>Family</th>
                                    <th>Tier</th>
                                    <th>Preflight</th>
                                    <th>Pareto</th>
                                    <th>Sharpe</th>
                                    <th>Fitness</th>
                                    <th>Turnover</th>
                                    <th>Margin</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rows}
                            </tbody>
                        </table>
                    </div>
                ` : `
                    <div style="text-align: center; padding: 40px; color: var(--text-muted);">
                        <i data-lucide="box" style="width: 32px; height: 32px; margin-bottom: 8px;"></i>
                        <p>No candidates generated yet. Use the Alpha Lab or Generator to synthesize candidates.</p>
                    </div>
                `}
            </div>
        `;

        if (window.lucide) window.lucide.createIcons();
    } catch (err) {
        container.innerHTML = `<div class="card" style="color: var(--status-danger);">Error: ${err.message}</div>`;
    }
}

export async function populateCandidateModal(candidateId) {
    const body = document.getElementById("candidate-modal-body");
    if (!body) return;

    body.innerHTML = `<div style="text-align: center; padding: 20px;"><i data-lucide="loader" class="spin"></i> Loading inspection details...</div>`;
    if (window.lucide) window.lucide.createIcons();

    try {
        const c = await api.getCandidateDetail(candidateId);
        const latestSim = c.simulations.length > 0 ? c.simulations[c.simulations.length - 1] : null;

        body.innerHTML = `
            <!-- Expression Box -->
            <div style="margin-bottom: 16px;">
                <label style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-muted);">Alpha Expression Code:</label>
                <div class="code-expr" style="display: block; max-width: 100%; font-size: 13px; margin-top: 4px; padding: 10px;">${c.expression}</div>
            </div>

            <!-- Metadata Grid -->
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;">
                <div class="card" style="margin: 0; padding: 12px;">
                    <div style="font-size: 11px; color: var(--text-muted);">Research Family</div>
                    <div style="font-weight: 700; font-size: 14px;">${c.family_code}</div>
                </div>
                <div class="card" style="margin: 0; padding: 12px;">
                    <div style="font-size: 11px; color: var(--text-muted);">Candidate Tier</div>
                    <div>${renderBadge(c.tier)}</div>
                </div>
                <div class="card" style="margin: 0; padding: 12px;">
                    <div style="font-size: 11px; color: var(--text-muted);">Complexity Score</div>
                    <div style="font-weight: 700; font-size: 14px;">${c.complexity_score}</div>
                </div>
            </div>

            <!-- Preflight & Diagnostic Attributes -->
            <div class="card" style="background-color: var(--bg-main); margin-bottom: 16px;">
                <h4 style="font-size: 13px; font-weight: 700; margin-bottom: 8px;"><i data-lucide="check-square"></i> Preflight Inspection Metrics</h4>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; font-size: 13px;">
                    <div><strong>Preflight:</strong> ${renderBadge(c.preflight.decision)}</div>
                    <div><strong>Temporal Compat:</strong> ${(c.compatibility_score * 100).toFixed(0)}%</div>
                    <div><strong>Constant Risk:</strong> ${(c.constant_signal_risk * 100).toFixed(0)}%</div>
                </div>
            </div>

            <!-- Performance Metrics -->
            <div class="card" style="margin-bottom: 16px;">
                <h4 style="font-size: 13px; font-weight: 700; margin-bottom: 8px;"><i data-lucide="bar-chart-2"></i> WorldQuant BRAIN Simulation Metrics</h4>
                ${latestSim ? `
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; font-size: 14px;">
                        <div><div style="font-size: 11px; color: var(--text-muted);">Sharpe</div><strong>${formatMetric(latestSim.sharpe)}</strong></div>
                        <div><div style="font-size: 11px; color: var(--text-muted);">Fitness</div><strong>${formatMetric(latestSim.fitness)}</strong></div>
                        <div><div style="font-size: 11px; color: var(--text-muted);">Turnover</div><strong>${formatMetric(latestSim.turnover)}</strong></div>
                        <div><div style="font-size: 11px; color: var(--text-muted);">Margin</div><strong>${formatBps(latestSim.margin_bps)}</strong></div>
                    </div>
                ` : `
                    <div style="color: var(--text-muted); font-size: 13px;">No simulation results recorded yet.</div>
                `}
            </div>

            <!-- Actions & Targeted Mutation -->
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <button class="btn btn-outline" id="btn-modal-mutate">
                    <i data-lucide="git-branch"></i> Generate Near-Miss Mutations
                </button>
                <div style="display: flex; gap: 8px;">
                    <button class="btn btn-primary" onclick="window.verdeUI.simulateCandidate('${c.id}')">
                        <i data-lucide="play"></i> Simulate on BRAIN
                    </button>
                </div>
            </div>

            <div id="mutation-results" style="margin-top: 16px;"></div>
        `;

        if (window.lucide) window.lucide.createIcons();

        document.getElementById("btn-modal-mutate")?.addEventListener("click", async () => {
            const mutContainer = document.getElementById("mutation-results");
            mutContainer.innerHTML = `<div style="padding: 10px;"><i data-lucide="loader" class="spin"></i> Synthesizing targeted mutations...</div>`;
            if (window.lucide) window.lucide.createIcons();

            try {
                const res = await api.mutateCandidate(c.id);
                mutContainer.innerHTML = `
                    <div class="card" style="background-color: var(--verde-pale); border-color: var(--verde-pale-border);">
                        <h4 style="font-size: 13px; font-weight: 700; margin-bottom: 8px;">Generated Mutations:</h4>
                        ${res.mutations.map(m => `
                            <div style="margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid rgba(0,0,0,0.05);">
                                <span class="badge badge-info">${m.mutation_type}</span>
                                <div class="code-expr" style="display: block; margin: 4px 0;">${m.expression}</div>
                                <div style="font-size: 12px; color: var(--text-muted);">${m.generation_reason}</div>
                            </div>
                        `).join('')}
                    </div>
                `;
            } catch (e) {
                mutContainer.innerHTML = `<div style="color: var(--status-danger);">Mutation failed: ${e.message}</div>`;
            }
        });

    } catch (err) {
        body.innerHTML = `<div style="color: var(--status-danger);">Error: ${err.message}</div>`;
    }
}
