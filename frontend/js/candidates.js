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

    body.innerHTML = `<div style="text-align: center; padding: 40px; color: var(--text-muted);"><i data-lucide="loader" class="spin" style="width: 28px; height: 28px; margin-bottom: 10px; color: var(--verde-primary);"></i><div>Loading candidate inspection details...</div></div>`;
    if (window.lucide) window.lucide.createIcons();

    try {
        const c = await api.getCandidateDetail(candidateId);
        const latestSim = c.simulations && c.simulations.length > 0 ? c.simulations[c.simulations.length - 1] : null;

        const isPareto = c.is_pareto;
        const tierBadge = renderBadge(c.tier);
        const preflightBadge = renderBadge(c.preflight ? c.preflight.decision : c.preflight_status || "PASS");

        body.innerHTML = `
            <!-- Top Summary Header -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 14px; border-bottom: 1px solid var(--border-color); flex-wrap: wrap; gap: 10px;">
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <span style="font-family: monospace; font-size: 13px; font-weight: 700; color: var(--verde-dark); background: var(--verde-pale); padding: 4px 10px; border-radius: var(--radius-sm); border: 1px solid var(--verde-pale-border);">
                        ${c.id.substring(0, 13)}
                    </span>
                    <span class="badge badge-info"><i data-lucide="tag" style="width: 12px; height: 12px;"></i> ${c.family_code || 'MOMENTUM'}</span>
                    ${tierBadge}
                    ${isPareto ? `<span class="badge badge-pareto"><i data-lucide="sparkles" style="width: 12px; height: 12px;"></i> Pareto Optimal</span>` : ''}
                </div>
                <div style="font-size: 12px; color: var(--text-muted);">
                    Created: ${formatTimestamp(c.created_at)}
                </div>
            </div>

            <!-- Alpha Expression Code Container with Copy Button -->
            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <label style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.3px;">
                        Alpha FastExpr Formula
                    </label>
                    <button class="btn btn-outline btn-sm" id="btn-copy-expr" style="font-size: 11px; padding: 3px 8px;" title="Copy Formula">
                        <i data-lucide="copy" style="width: 12px; height: 12px;"></i> Copy Code
                    </button>
                </div>
                <div class="code-expr" style="display: block; width: 100%; font-size: 13px; padding: 14px; line-height: 1.6; word-break: break-all; border-radius: var(--radius-md); box-sizing: border-box; background: var(--bg-card-dark-gradient); color: #f1f5f9; border: 1px solid rgba(34, 197, 94, 0.3);">
                    ${c.expression}
                </div>
            </div>

            <!-- Simulation Performance Metric Cards -->
            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-size: 13px; font-weight: 700; color: var(--text-main); display: flex; align-items: center; gap: 6px;">
                        <i data-lucide="activity" style="color: var(--verde-primary);"></i> BRAIN Performance & Metrics
                    </span>
                    ${latestSim ? renderBadge(latestSim.status) : '<span style="font-size: 12px; color: var(--text-muted);">Not Simulated</span>'}
                </div>
                ${latestSim && (latestSim.sharpe !== null || latestSim.fitness !== null) ? `
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
                        <div class="card" style="margin: 0; padding: 14px; text-align: center; border-top: 3px solid #16a34a; background: #fafafa;">
                            <div style="font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Sharpe Ratio</div>
                            <div style="font-size: 20px; font-weight: 800; color: #16a34a; margin-top: 4px;">${formatMetric(latestSim.sharpe)}</div>
                            <div style="font-size: 10.5px; color: var(--text-muted); margin-top: 2px;">Target ≥ 1.25</div>
                        </div>
                        <div class="card" style="margin: 0; padding: 14px; text-align: center; border-top: 3px solid #16a34a; background: #fafafa;">
                            <div style="font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Fitness</div>
                            <div style="font-size: 20px; font-weight: 800; color: #16a34a; margin-top: 4px;">${formatMetric(latestSim.fitness)}</div>
                            <div style="font-size: 10.5px; color: var(--text-muted); margin-top: 2px;">Target ≥ 1.00</div>
                        </div>
                        <div class="card" style="margin: 0; padding: 14px; text-align: center; border-top: 3px solid #3b82f6; background: #fafafa;">
                            <div style="font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Turnover</div>
                            <div style="font-size: 20px; font-weight: 800; color: #3b82f6; margin-top: 4px;">${formatMetric(latestSim.turnover)}</div>
                            <div style="font-size: 10.5px; color: var(--text-muted); margin-top: 2px;">Max ≤ 0.70</div>
                        </div>
                        <div class="card" style="margin: 0; padding: 14px; text-align: center; border-top: 3px solid #eab308; background: #fafafa;">
                            <div style="font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Margin</div>
                            <div style="font-size: 20px; font-weight: 800; color: #ca8a04; margin-top: 4px;">${formatBps(latestSim.margin_bps)}</div>
                            <div style="font-size: 10.5px; color: var(--text-muted); margin-top: 2px;">Min ≥ 4.0 bps</div>
                        </div>
                    </div>
                ` : `
                    <div class="card" style="margin: 0; padding: 18px; text-align: center; background: #f8fafc;">
                        <i data-lucide="play-circle" style="width: 24px; height: 24px; color: var(--text-muted); margin-bottom: 6px;"></i>
                        <div style="font-size: 13px; font-weight: 600; color: var(--text-main);">No simulation metrics recorded yet.</div>
                        <div style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">Submit candidate to BRAIN to calculate Sharpe, Fitness, and Turnover metrics.</div>
                    </div>
                `}
            </div>

            <!-- Preflight & AST Architecture Details -->
            <div class="card" style="margin-bottom: 20px; padding: 18px; background: #ffffff;">
                <h4 style="font-size: 13px; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                    <i data-lucide="shield-check" style="color: var(--verde-primary);"></i> Pre-BRAIN Quality Score & AST Architecture
                </h4>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; font-size: 13px; margin-bottom: 14px;">
                    <div>
                        <div style="font-size: 11px; color: var(--text-muted); font-weight: 600;">Pre-BRAIN Score</div>
                        <div style="font-size: 15px; font-weight: 800; color: ${c.pre_brain_score >= 75 ? '#16a34a' : (c.pre_brain_score >= 65 ? '#ca8a04' : '#ef4444')}; margin-top: 2px;">
                            ${c.pre_brain_score !== null && c.pre_brain_score !== undefined ? `${c.pre_brain_score}/100` : 'N/A'}
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: var(--text-muted); font-weight: 600;">Lifecycle State</div>
                        <div style="margin-top: 2px;">
                            <span class="badge badge-success" style="font-size: 11px;">${c.lifecycle_state || 'PREFLIGHT'}</span>
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: var(--text-muted); font-weight: 600;">Strategy Allocation</div>
                        <div style="font-size: 13px; font-weight: 700; color: var(--text-main); margin-top: 2px;">
                            ${c.priority_bucket || 'EXPLOITATION'}
                        </div>
                    </div>
                </div>

                ${c.explainability_rationale && c.explainability_rationale.field_selection_rationale ? `
                    <div style="background: #f8fafc; padding: 12px 14px; border-radius: var(--radius-sm); border: 1px solid var(--border-light); font-size: 12px; color: var(--text-main);">
                        <div style="font-weight: 700; color: var(--verde-dark); margin-bottom: 4px; display: flex; align-items: center; gap: 4px;">
                            <i data-lucide="help-circle" style="width: 13px; height: 13px;"></i> WHY THIS ALPHA?
                        </div>
                        <div style="margin-bottom: 3px;"><strong>Hypothesis:</strong> ${c.explainability_rationale.hypothesis || 'N/A'}</div>
                        <div style="margin-bottom: 3px;"><strong>Field Rationale:</strong> ${c.explainability_rationale.field_selection_rationale}</div>
                        <div><strong>Operator Rationale:</strong> ${c.explainability_rationale.operator_rationale}</div>
                    </div>
                ` : ''}
            </div>
                    <div style="padding: 10px; background: #f8fafc; border-radius: var(--radius-sm);">
                        <div style="font-size: 11px; color: var(--text-muted);">Preflight Decision</div>
                        <div style="margin-top: 4px;">${preflightBadge}</div>
                    </div>
                    <div style="padding: 10px; background: #f8fafc; border-radius: var(--radius-sm);">
                        <div style="font-size: 11px; color: var(--text-muted);">Temporal Compatibility</div>
                        <div style="font-weight: 700; font-size: 14px; color: #16a34a; margin-top: 4px;">
                            ${((c.compatibility_score || 1.0) * 100).toFixed(0)}%
                        </div>
                    </div>
                    <div style="padding: 10px; background: #f8fafc; border-radius: var(--radius-sm);">
                        <div style="font-size: 11px; color: var(--text-muted);">Constant Signal Risk</div>
                        <div style="font-weight: 700; font-size: 14px; color: ${(c.constant_signal_risk || 0) > 0.3 ? '#ef4444' : '#16a34a'}; margin-top: 4px;">
                            ${((c.constant_signal_risk || 0.0) * 100).toFixed(0)}%
                        </div>
                    </div>
                </div>

                <!-- Fields and Operators Chips -->
                <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--border-light); display: flex; flex-wrap: wrap; gap: 16px; font-size: 12.5px;">
                    <div>
                        <strong style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">Fields Used:</strong>
                        <div style="display: flex; gap: 4px; flex-wrap: wrap; margin-top: 4px;">
                            ${(c.fields_used || []).map(f => `<span class="badge badge-info">${f}</span>`).join('') || '<span style="color: var(--text-muted);">None</span>'}
                        </div>
                    </div>
                    <div>
                        <strong style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">Operators Used:</strong>
                        <div style="display: flex; gap: 4px; flex-wrap: wrap; margin-top: 4px;">
                            ${(c.operators_used || []).map(o => `<span class="badge badge-warning">${o}</span>`).join('') || '<span style="color: var(--text-muted);">None</span>'}
                        </div>
                    </div>
                    <div>
                        <strong style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">AST Complexity:</strong>
                        <div style="margin-top: 4px; font-weight: 700;">Score: ${c.complexity_score || 1.0} (Depth: ${c.nesting_depth || 1})</div>
                    </div>
                </div>
            </div>

            <!-- Action Bar -->
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                <button class="btn btn-outline" id="btn-modal-mutate">
                    <i data-lucide="git-branch"></i> Synthesize Near-Miss Mutations
                </button>
                <div style="display: flex; gap: 8px;">
                    <button class="btn btn-outline" onclick="window.verdeUI.closeCandidateModal()">
                        Close
                    </button>
                    <button class="btn btn-primary" onclick="window.verdeUI.closeCandidateModal(); window.verdeUI.simulateCandidate('${c.id}')">
                        <i data-lucide="play"></i> Simulate on BRAIN
                    </button>
                </div>
            </div>

            <!-- Mutation Container -->
            <div id="mutation-results" style="margin-top: 16px;"></div>
        `;

        if (window.lucide) window.lucide.createIcons();

        // Copy expression button
        document.getElementById("btn-copy-expr")?.addEventListener("click", () => {
            navigator.clipboard.writeText(c.expression).then(() => {
                showToast("Alpha expression copied to clipboard!", "success");
            }).catch(() => {
                showToast("Failed to copy to clipboard", "error");
            });
        });

        // Mutate handler
        document.getElementById("btn-modal-mutate")?.addEventListener("click", async () => {
            const mutBtn = document.getElementById("btn-modal-mutate");
            const mutContainer = document.getElementById("mutation-results");
            if (mutBtn) {
                mutBtn.disabled = true;
                mutBtn.innerHTML = `<i data-lucide="loader" class="spin"></i> Synthesizing...`;
            }
            mutContainer.innerHTML = `<div style="text-align: center; padding: 20px; color: var(--text-muted);"><i data-lucide="loader" class="spin"></i> Synthesizing & preflighting targeted mutations...</div>`;
            if (window.lucide) window.lucide.createIcons();

            try {
                const res = await api.mutateCandidate(c.id);
                showToast(`Synthesized ${res.mutations.length} near-miss hypothesis mutations.`, "success");
                
                mutContainer.innerHTML = `
                    <div class="card" style="background-color: var(--verde-pale); border-color: var(--verde-pale-border); margin-top: 12px;">
                        <h4 style="font-size: 13px; font-weight: 700; color: var(--verde-dark); margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                            <i data-lucide="git-commit"></i> Generated Hypothesis Mutations (${res.mutations.length})
                        </h4>
                        <div style="display: flex; flex-direction: column; gap: 10px;">
                            ${res.mutations.map(m => `
                                <div style="background: #ffffff; padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--verde-pale-border);">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                        <div style="display: flex; align-items: center; gap: 6px;">
                                            <span class="badge badge-info">${m.mutation_type}</span>
                                            ${renderBadge(m.preflight_status || 'PASS')}
                                        </div>
                                        <button class="btn btn-primary btn-sm" onclick="window.verdeUI.closeCandidateModal(); window.verdeUI.simulateCandidate('${m.candidate_id}')" style="font-size: 11px; padding: 3px 8px;">
                                            <i data-lucide="play" style="width: 11px; height: 11px;"></i> Simulate Variant
                                        </button>
                                    </div>
                                    <div class="code-expr" style="display: block; margin: 6px 0; font-size: 12px;">${m.expression}</div>
                                    <div style="font-size: 11.5px; color: var(--text-muted);">${m.generation_reason}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
                if (window.lucide) window.lucide.createIcons();
            } catch (e) {
                mutContainer.innerHTML = `<div class="card" style="color: var(--status-danger);">Mutation generation notice: ${e.message}</div>`;
                showToast(`Mutation failed: ${e.message}`, "error");
            } finally {
                if (mutBtn) {
                    mutBtn.disabled = false;
                    mutBtn.innerHTML = `<i data-lucide="git-branch"></i> Synthesize Near-Miss Mutations`;
                    if (window.lucide) window.lucide.createIcons();
                }
            }
        });

    } catch (err) {
        body.innerHTML = `<div class="card" style="color: var(--status-danger);">Error loading candidate details: ${err.message}</div>`;
    }
}
