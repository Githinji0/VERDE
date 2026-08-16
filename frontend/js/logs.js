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
        const isPortEmpty = s.classification === "PORTFOLIO_EMPTY" || s.portfolio_status === "EMPTY";
        const isTechFail = s.classification === "TECHNICAL_FAILURE" || s.classification === "REMOTE_FAILURE" || s.classification === "AUTH_FAILURE";
        
        const details = s.diagnostic_details || {};
        const rootCause = details.root_cause || { type: s.root_cause_type || 'UNVERIFIED', confidence: s.root_cause_confidence || 'LOW', message: s.possible_cause || s.diagnostic_reason };
        const evCat = details.evidence_categorized || {};
        const componentTests = details.component_tests || [];
        const pipeline = details.position_pipeline || {};
        const experiments = details.recommended_experiments || [];
        const whyNotProven = s.why_not_proven || details.why_not_proven || rootCause.why_not_proven;

        let bannerBg = 'rgba(234, 179, 8, 0.08)';
        let bannerBorder = 'var(--status-warning)';
        let bannerColor = '#ca8a04';
        let bannerIcon = 'alert-triangle';

        if (isTechFail) {
            bannerBg = 'rgba(239, 68, 68, 0.08)';
            bannerBorder = 'var(--status-danger)';
            bannerColor = 'var(--status-danger)';
            bannerIcon = 'alert-octagon';
        } else if (s.classification === 'VALID_METRICS') {
            bannerBg = 'rgba(22, 163, 74, 0.08)';
            bannerBorder = '#16a34a';
            bannerColor = '#16a34a';
            bannerIcon = 'check-circle';
        }

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
            <div class="diagnostic-banner" style="background: ${bannerBg}; border-left: 4px solid ${bannerBorder}; padding: 14px 16px; border-radius: var(--radius-sm); margin-bottom: 18px;">
                <div class="diagnostic-title" style="font-weight: 700; color: ${bannerColor}; font-size: 13px; display: flex; align-items: center; gap: 6px;">
                    <i data-lucide="${bannerIcon}" style="width: 16px; height: 16px;"></i>
                    Classification: ${s.classification} (Remote Status: ${s.remote_status || s.status})
                </div>
                <div class="diagnostic-detail" style="margin-top: 6px; font-size: 12.5px; line-height: 1.5; color: var(--text-main);">
                    ${s.diagnostic_reason || 'Simulation telemetry evaluated by VERDE diagnostic engine.'}
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
                    <div style="margin-top: 4px;">${renderBadge(s.remote_status || s.status)}</div>
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

            <!-- Root Cause & Diagnostic Hypothesis Card -->
            <div class="card" style="margin: 0 0 16px 0; padding: 14px; background: #ffffff;">
                <div style="font-size: 12.5px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">Most Likely Cause / Hypothesis:</strong>
                        <span class="badge ${rootCause.confidence === 'HIGH' ? 'badge-danger' : 'badge-warning'}" style="font-size: 10px;">
                            Confidence: ${rootCause.confidence || 'LOW'}
                        </span>
                    </div>
                    <div style="font-weight: 700; color: var(--text-main); font-size: 13px; margin-top: 4px;">
                        ${rootCause.type || s.root_cause_type || 'UNVERIFIED_ROOT_CAUSE'}
                    </div>
                    <p style="margin-top: 4px; color: var(--text-main); font-size: 12.5px; line-height: 1.4;">
                        ${rootCause.message || s.possible_cause || 'Simulation completed without positions; underlying collapse mechanism unverified.'}
                    </p>
                </div>

                <!-- Why This Is Not Proven Callout -->
                ${whyNotProven ? `
                    <div style="margin-top: 10px; padding: 10px 12px; background: #fffbebf5; border-left: 3px solid #f59e0b; border-radius: var(--radius-sm); font-size: 12px;">
                        <div style="font-weight: 700; color: #b45309; margin-bottom: 3px;">
                            <i data-lucide="help-circle" style="width: 13px; height: 13px; display: inline;"></i> Why This Is Not Proven
                        </div>
                        <div style="color: #78350f; line-height: 1.4;">
                            ${whyNotProven}
                        </div>
                    </div>
                ` : ''}

                <!-- Categorized Evidence Lists -->
                <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border-light);">
                    <strong style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">Evidence Levels:</strong>
                    <div style="display: flex; flex-direction: column; gap: 6px; margin-top: 6px; font-size: 12px;">
                        ${(evCat.observed || []).map(e => `
                            <div style="display: flex; align-items: flex-start; gap: 6px;">
                                <span class="badge badge-success" style="font-size: 9px; padding: 1px 5px;">OBSERVED</span>
                                <span>${e}</span>
                            </div>
                        `).join('')}
                        ${(evCat.proven || []).map(e => `
                            <div style="display: flex; align-items: flex-start; gap: 6px;">
                                <span class="badge badge-info" style="font-size: 9px; padding: 1px 5px;">PROVEN</span>
                                <span>${e}</span>
                            </div>
                        `).join('')}
                        ${(evCat.inferred || []).map(e => `
                            <div style="display: flex; align-items: flex-start; gap: 6px;">
                                <span class="badge badge-warning" style="font-size: 9px; padding: 1px 5px;">INFERRED</span>
                                <span>${e}</span>
                            </div>
                        `).join('')}
                        ${(evCat.possible || []).map(e => `
                            <div style="display: flex; align-items: flex-start; gap: 6px;">
                                <span class="badge badge-warning" style="font-size: 9px; padding: 1px 5px; background: #fef3c7; color: #92400e;">POSSIBLE</span>
                                <span>${e}</span>
                            </div>
                        `).join('')}
                        ${(evCat.unknown || []).map(e => `
                            <div style="display: flex; align-items: flex-start; gap: 6px;">
                                <span class="badge" style="font-size: 9px; padding: 1px 5px; background: #e2e8f0; color: #475569;">UNKNOWN</span>
                                <span style="color: var(--text-muted);">${e}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- Position Pipeline Stage Breakdown -->
                ${pipeline.last_nonzero_stage ? `
                    <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border-light);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <strong style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">Position Construction Pipeline:</strong>
                            <span style="font-size: 11px; color: var(--text-muted);">Last Nonzero: <strong>${pipeline.last_nonzero_stage}</strong></span>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; font-size: 11px;">
                            <div style="padding: 6px; background: #f8fafc; border-radius: 4px; border: 1px solid var(--border-light);">
                                <span style="color: var(--text-muted); display: block;">Universe</span>
                                <strong>${pipeline.universe_count ?? 3000}</strong>
                            </div>
                            <div style="padding: 6px; background: #f8fafc; border-radius: 4px; border: 1px solid var(--border-light);">
                                <span style="color: var(--text-muted); display: block;">Post-Neutralization</span>
                                <strong>${pipeline.post_neutralization_weights}</strong>
                            </div>
                            <div style="padding: 6px; background: #f8fafc; border-radius: 4px; border: 1px solid var(--border-light);">
                                <span style="color: var(--text-muted); display: block;">Post-Truncation</span>
                                <strong>${pipeline.post_truncation_weights}</strong>
                            </div>
                            <div style="padding: 6px; background: #f8fafc; border-radius: 4px; border: 1px solid var(--border-light);">
                                <span style="color: var(--text-muted); display: block;">Final Positions</span>
                                <strong>${pipeline.final_positions ?? 0}</strong>
                            </div>
                        </div>
                    </div>
                ` : ''}

                <!-- Component Hierarchy -->
                ${componentTests.length > 0 ? `
                    <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border-light);">
                        <strong style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">Expression Component Hierarchy:</strong>
                        <div style="margin-top: 6px; display: flex; flex-direction: column; gap: 6px;">
                            ${componentTests.map(t => `
                                <div style="font-size: 11.5px; background: #f8fafc; padding: 6px 10px; border-radius: 4px; border: 1px solid var(--border-light); display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <code style="font-size: 11px; font-weight: 700; color: var(--verde-primary);">${t.expression}</code>
                                        <span style="color: var(--text-muted); margin-left: 6px;">(${t.stage})</span>
                                    </div>
                                    <span class="badge ${t.status === 'VALID' ? 'badge-success' : 'badge-warning'}" style="font-size: 10px;">
                                        ${t.status}
                                    </span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                <!-- Configuration Summary -->
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; font-size: 12px; margin-top: 12px; padding-top: 8px; border-top: 1px solid var(--border-light);">
                    <div><span style="color: var(--text-muted);">Universe:</span> <strong>${s.universe || 'TOP3000'}</strong></div>
                    <div><span style="color: var(--text-muted);">Region:</span> <strong>${s.region || 'USA'}</strong></div>
                    <div><span style="color: var(--text-muted);">Delay:</span> <strong>${s.delay ?? 1}</strong></div>
                    <div><span style="color: var(--text-muted);">Neutralization:</span> <strong>${s.neutralization || 'SUBINDUSTRY'}</strong></div>
                </div>
            </div>

            <!-- Recommended Control Experiments Card -->
            ${experiments.length > 0 ? `
                <div class="card" style="margin: 0 0 16px 0; padding: 14px; background: #f8fafc; border: 1px solid #cbd5e1;">
                    <div style="font-size: 12px; font-weight: 700; color: var(--text-main); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
                        <i data-lucide="flask-conical" style="width: 14px; height: 14px; color: var(--verde-primary);"></i> Recommended Control Experiments (A/B Testing)
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        ${experiments.map(exp => `
                            <div style="background: #ffffff; padding: 8px 12px; border-radius: 4px; border: 1px solid var(--border-light); font-size: 12px;">
                                <div style="font-weight: 700; color: var(--text-main);">${exp.name}</div>
                                <div style="margin-top: 2px;"><code style="font-size: 11px; color: var(--verde-primary);">${exp.expression}</code></div>
                                <div style="font-size: 11px; color: var(--text-muted); margin-top: 3px;">
                                    Setting: Neutralization = <strong>${exp.neutralization}</strong> — ${exp.notes}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}

            <!-- Raw Response Viewer (Collapsible & Sanitized) -->
            ${s.raw_response ? `
                <div style="margin-bottom: 18px;">
                    <details style="background: #0f172a; border-radius: var(--radius-sm); padding: 10px; color: #cbd5e1; font-size: 11.5px;">
                        <summary style="cursor: pointer; font-weight: 600; color: #94a3b8; user-select: none;">
                            <i data-lucide="code" style="width: 12px; height: 12px; display: inline;"></i> View Raw API Response Telemetry (Credentials Redacted)
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
