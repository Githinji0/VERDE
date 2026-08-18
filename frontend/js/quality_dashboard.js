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

    document.getElementById("btn-new-experiment")?.addEventListener("click", createNewExperimentPrompt);
}

async function loadQualitySummary() {
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

async function loadExperimentsList() {
    const container = document.getElementById("experiments-list-container");
    if (!container) return;
    try {
        const exps = await api.get("/api/research/experiments");
        if (exps.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 24px; color: var(--text-muted);">
                    <p style="font-size: 13px;">No research experiments started yet.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = exps.map(e => `
            <div style="padding: 12px 14px; border: 1px solid var(--border-light); border-radius: var(--radius-md); margin-bottom: 10px; background: #ffffff;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="font-size: 13.5px; color: var(--text-main);">${e.title}</strong>
                    <span class="badge badge-success" style="font-size: 10.5px;">${e.status}</span>
                </div>
                <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">${e.hypothesis}</div>
                <div style="display: flex; gap: 14px; margin-top: 8px; font-size: 11.5px; color: var(--text-muted);">
                    <span>Generated: <strong>${e.candidates_generated}/${e.target_budget}</strong></span>
                    <span>Rejected: <strong style="color: #ef4444;">${e.candidates_rejected_preflight}</strong></span>
                    <span>Elite: <strong style="color: #22c55e;">${e.elite_alpha_count}</strong></span>
                </div>
            </div>
        `).join('');
    } catch (e) {
        container.innerHTML = `<div style="color: var(--status-danger); font-size: 12px;">Failed to load experiments.</div>`;
    }
}

async function loadResearchGaps() {
    const container = document.getElementById("research-gaps-container");
    if (!container) return;
    try {
        const gaps = await api.get("/api/research/gaps");
        const underexplored = gaps.underexplored_families || [];
        if (underexplored.length === 0) {
            container.innerHTML = `
                <div style="padding: 10px; background: #f0fdf4; border-radius: var(--radius-sm); border: 1px solid rgba(34, 197, 94, 0.2); color: #16a34a; font-size: 12px;">
                    <i data-lucide="check-circle" style="width: 14px; height: 14px; display: inline;"></i> All 15 research families have broad candidate coverage.
                </div>
            `;
            if (window.lucide) window.lucide.createIcons();
            return;
        }

        container.innerHTML = `
            <div style="margin-bottom: 8px; font-weight: 700; font-size: 12px; color: var(--text-muted);">Recommended Exploration Allocation:</div>
            ${underexplored.slice(0, 3).map(g => `
                <div style="padding: 8px 10px; background: #fffbe6; border: 1px solid rgba(234, 179, 8, 0.3); border-radius: var(--radius-sm); margin-bottom: 6px; font-size: 12px;">
                    <strong style="color: #ca8a04;">${g.family_code}</strong>: ${g.reason}
                </div>
            `).join('')}
        `;
        if (window.lucide) window.lucide.createIcons();
    } catch (e) {
        container.innerHTML = `<div style="color: var(--text-muted); font-size: 12px;">No research gaps detected.</div>`;
    }
}

async function createNewExperimentPrompt() {
    const title = prompt("Enter Experiment Title:", "Medium-Term Momentum Research Run");
    if (!title) return;
    try {
        await api.post("/api/research/experiments", {
            title: title,
            hypothesis: "Medium-term momentum signals across liquid universe",
            family_code: "MOMENTUM",
            target_budget: 20
        });
        alert("Experiment started successfully!");
        loadExperimentsList();
        loadQualitySummary();
    } catch (e) {
        alert("Error starting experiment: " + e.message);
    }
}
