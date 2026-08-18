import { api } from './api.js';

export async function renderQualityDashboard(container) {
    container.innerHTML = `
        <!-- Top Stats Telemetry Ribbon -->
        <div class="telemetry-ribbon-container" style="margin-bottom: 20px;">
            <div class="telemetry-badge-hero">
                <div class="pulse-indicator">
                    <span class="pulse-dot"></span>
                    <span class="pulse-ring"></span>
                </div>
                <div class="telemetry-hero-details">
                    <span class="telemetry-label">Preflight Rejection</span>
                    <span class="telemetry-value" id="quality-preflight-rate">-</span>
                </div>
            </div>

            <div class="telemetry-yield-wrapper">
                <div class="yield-bar-header">
                    <span class="yield-bar-title"><i data-lucide="shield-check"></i> BRAIN Submission Efficiency</span>
                    <span class="yield-bar-percentage" id="quality-efficiency-text">100% Filter Quality</span>
                </div>
                <div class="yield-progress-bar">
                    <div class="yield-segment segment-valid" id="q-bar-valid" style="width: 70%;" title="Passed Preflight"></div>
                    <div class="yield-segment segment-failed" id="q-bar-rejected" style="width: 30%;" title="Rejected Preflight (<65 Score)"></div>
                </div>
            </div>

            <div class="telemetry-chips-group">
                <div class="telemetry-chip active">
                    <i data-lucide="award" style="color: #22c55e;"></i>
                    <span class="chip-label">Elite Alphas</span>
                    <span class="chip-count" id="q-count-elite">-</span>
                </div>
                <div class="telemetry-chip">
                    <i data-lucide="star" style="color: #ca8a04;"></i>
                    <span class="chip-label">Strong Alphas</span>
                    <span class="chip-count" id="q-count-strong">-</span>
                </div>
            </div>
        </div>

        <!-- Two Column Layout -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
            <!-- Left Card: Research Experiments & Controls -->
            <div class="card">
                <div class="card-header">
                    <div>
                        <h3 class="card-title"><i data-lucide="flask-conical" style="color: var(--verde-primary);"></i> Active Research Experiments</h3>
                        <span class="card-subtitle">Hypothesis-driven research allocations and strategy budgets</span>
                    </div>
                    <button class="btn btn-primary btn-sm" id="btn-new-experiment">
                        <i data-lucide="plus"></i> New Experiment
                    </button>
                </div>
                <div id="experiments-list-container">
                    <div style="text-align: center; padding: 30px; color: var(--text-muted);">
                        <i data-lucide="loader" class="spin" style="width: 20px; height: 20px; margin-bottom: 6px;"></i>
                        <div>Loading experiments...</div>
                    </div>
                </div>
            </div>

            <!-- Right Card: Quality Benchmark & Research Gaps -->
            <div style="display: flex; flex-direction: column; gap: 20px;">
                <!-- Benchmark Card -->
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title"><i data-lucide="trending-up" style="color: #22c55e;"></i> Quality Benchmark (V1 vs V2)</h3>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; background: #f8fafc; padding: 16px; border-radius: var(--radius-md); border: 1px solid var(--border-light);">
                        <div style="border-right: 1px solid var(--border-light); padding-right: 10px;">
                            <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Before V2 Engine</div>
                            <div style="font-size: 18px; font-weight: 800; color: #ef4444; margin-top: 4px;">100.0% Submitted</div>
                            <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">Random / Static Templates</div>
                            <div style="font-size: 11px; color: var(--text-muted);">34.0% Portfolio Success</div>
                        </div>
                        <div>
                            <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">After V2 Quality Engine</div>
                            <div style="font-size: 18px; font-weight: 800; color: #22c55e; margin-top: 4px;" id="benchmark-efficiency">-</div>
                            <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">8-Dim Preflight Quality Score (<65 Rejected)</div>
                            <div style="font-size: 11px; color: #22c55e; font-weight: 700;" id="benchmark-success">-</div>
                        </div>
                    </div>
                </div>

                <!-- Research Gaps Card -->
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title"><i data-lucide="compass" style="color: #ca8a04;"></i> Automatic Research Gap Detection</h3>
                    </div>
                    <div id="research-gaps-container" style="font-size: 13px; color: var(--text-main);">
                        <div style="text-align: center; padding: 20px; color: var(--text-muted);">
                            <i data-lucide="loader" class="spin" style="width: 18px; height: 18px; margin-bottom: 6px;"></i>
                            <div>Scanning research database for gaps...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    // Fetch and update data
    await loadQualitySummary();
    await loadExperimentsList();
    await loadResearchGaps();

    document.getElementById("btn-new-experiment")?.addEventListener("click", () => {
        if (window.verdeUI && window.verdeUI.openNewExperimentModal) {
            window.verdeUI.openNewExperimentModal();
        }
    });
}

export async function loadQualitySummary() {
    try {
        const summary = await api.get("/api/research/quality-summary");
        const pRate = document.getElementById("quality-preflight-rate");
        const cElite = document.getElementById("q-count-elite");
        const cStrong = document.getElementById("q-count-strong");
        const bEff = document.getElementById("benchmark-efficiency");
        const bSucc = document.getElementById("benchmark-success");

        if (pRate) pRate.textContent = summary.preflight_rejection_rate;
        if (cElite) cElite.textContent = summary.elite_alpha_count;
        if (cStrong) cStrong.textContent = summary.strong_alpha_count;
        if (bEff) bEff.textContent = `${summary.brain_submission_efficiency} Submitted`;
        if (bSucc) bSucc.textContent = `${summary.portfolio_success_rate} Portfolio Success`;
    } catch (e) {
        console.warn("Error loading quality summary:", e);
    }
}

export async function loadExperimentsList() {
    const container = document.getElementById("experiments-list-container");
    if (!container) return;
    try {
        const exps = await api.get("/api/research/experiments");
        if (!exps || exps.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 24px; color: var(--text-muted);">
                    <p style="font-size: 13px;">No research experiments started yet.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = exps.map(e => {
            const hyp = e.structured_hypothesis || {};
            const reqQuestion = hyp.research_question || e.hypothesis;
            const statusClass = e.status === "COMPLETED" ? "badge-success" : (e.status.includes("FAILED") ? "badge-danger" : "badge-info");
            
            // Build 7-stage progress indicator
            const stages = [
                { name: "HYPOTHESIS", done: true },
                { name: "GENERATION", done: e.candidates_generated > 0 },
                { name: "VALIDATION", done: e.candidates_validated > 0 },
                { name: "EVALUATION", done: e.candidates_evaluated > 0 },
                { name: "QUALITY", done: (e.candidates_rejected + e.candidates_promising + e.elite_alpha_count) > 0 },
                { name: "RESEARCH REVIEW", done: e.status === "COMPLETED" },
                { name: "SUBMISSION", done: e.candidates_submitted > 0 }
            ];

            const progressHtml = stages.map((s, idx) => `
                <div style="display: flex; align-items: center; gap: 4px; font-size: 10px; font-weight: 700; color: ${s.done ? 'var(--verde-primary, #22c55e)' : '#94a3b8'};">
                    <span>${s.name}</span>
                    <span style="font-size: 11px;">${s.done ? '✓' : '○'}</span>
                    ${idx < stages.length - 1 ? '<span style="color: #cbd5e1; margin: 0 2px;">→</span>' : ''}
                </div>
            `).join('');

            return `
                <div onclick="window.verdeUI.openExperimentInspectorModal('${e.id}')" style="padding: 16px 18px; border: 1px solid var(--border-light); border-radius: var(--radius-md); margin-bottom: 12px; background: #ffffff; cursor: pointer; transition: all 0.2s ease; box-shadow: var(--shadow-card);" onmouseover="this.style.borderColor='var(--verde-primary)';" onmouseout="this.style.borderColor='var(--border-light)';">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                        <div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <strong style="font-size: 14px; color: var(--text-main);">${e.title}</strong>
                                <span class="badge" style="background: #f1f5f9; color: #475569; font-size: 10px; font-weight: 700;">${e.family_code}</span>
                            </div>
                            <div style="font-size: 12px; font-weight: 600; color: #0284c7; margin-top: 3px;">Q: "${reqQuestion}"</div>
                        </div>
                        <span class="badge ${statusClass}" style="font-size: 10.5px; font-weight: 700;">${e.status}</span>
                    </div>

                    <!-- Multi-Stage Progress Ribbon -->
                    <div style="display: flex; flex-wrap: wrap; gap: 6px; padding: 6px 10px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid #f1f5f9; margin: 10px 0;">
                        ${progressHtml}
                    </div>

                    <!-- Granular Candidate Funnel Statistics Grid -->
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 10px; padding-top: 10px; border-top: 1px dashed var(--border-light); font-size: 11.5px; text-align: center;">
                        <div style="background: #f8fafc; padding: 6px 4px; border-radius: 4px;">
                            <span style="color: var(--text-muted); display: block; font-size: 10px;">GENERATED</span>
                            <strong>${e.candidates_generated}</strong>
                        </div>
                        <div style="background: #f8fafc; padding: 6px 4px; border-radius: 4px;">
                            <span style="color: var(--text-muted); display: block; font-size: 10px;">EVALUATED</span>
                            <strong style="color: #0284c7;">${e.candidates_evaluated}</strong>
                        </div>
                        <div style="background: #f8fafc; padding: 6px 4px; border-radius: 4px;">
                            <span style="color: var(--text-muted); display: block; font-size: 10px;">REJECTED</span>
                            <strong style="color: #ef4444;">${e.candidates_rejected}</strong>
                        </div>
                        <div style="background: #f8fafc; padding: 6px 4px; border-radius: 4px;">
                            <span style="color: var(--text-muted); display: block; font-size: 10px;">PROMISING / ELITE</span>
                            <strong style="color: #22c55e;">${e.candidates_promising} / ${e.elite_alpha_count}</strong>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (e) {
        console.error("Failed to load experiments list:", e);
        container.innerHTML = `<div style="color: var(--status-danger); font-size: 12px;">Failed to load experiments.</div>`;
    }
}

export async function loadResearchGaps() {
    const container = document.getElementById("research-gaps-container");
    if (!container) return;
    try {
        const gaps = await api.get("/api/research/gaps");
        const underexplored = gaps.underexplored_gaps || gaps.underexplored_families || [];
        const allocations = gaps.research_allocation || {};

        if (underexplored.length === 0) {
            container.innerHTML = `
                <div style="padding: 10px; background: #f0fdf4; border-radius: var(--radius-sm); border: 1px solid rgba(34, 197, 94, 0.2); color: #16a34a; font-size: 12px;">
                    <i data-lucide="check-circle" style="width: 14px; height: 14px; display: inline;"></i> All research families have active evidence-backed candidate coverage.
                </div>
            `;
            if (window.lucide) window.lucide.createIcons();
            return;
        }

        container.innerHTML = `
            <div style="margin-bottom: 8px; font-weight: 700; font-size: 11.5px; color: var(--text-muted); text-transform: uppercase;">Evidence-Driven Gap Detection:</div>
            ${underexplored.slice(0, 3).map(g => `
                <div style="padding: 10px 12px; background: #fffbe6; border: 1px solid rgba(234, 179, 8, 0.3); border-radius: var(--radius-sm); margin-bottom: 8px; font-size: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="color: #ca8a04; font-size: 12.5px;">${g.family_code}</strong>
                        <span class="badge" style="background: #fef08a; color: #854d0e; font-size: 10px;">${allocations[g.family_code] || '25%'} Budget</span>
                    </div>
                    <div style="color: var(--text-muted); font-size: 11.5px; margin-top: 4px;">
                        Coverage: <strong>${g.coverage}</strong> &bull; Evaluated: <strong>${g.candidates_evaluated || 0}</strong> &bull; Elite: <strong>${g.elite_count || 0}</strong>
                    </div>
                    <div style="color: #854d0e; font-size: 11.5px; font-weight: 600; margin-top: 4px;">${g.recommendation}</div>
                </div>
            `).join('')}
        `;
        if (window.lucide) window.lucide.createIcons();
    } catch (e) {
        container.innerHTML = `<div style="color: var(--text-muted); font-size: 12px;">No research gaps detected.</div>`;
    }
}
