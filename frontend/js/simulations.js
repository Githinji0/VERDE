import { api } from './api.js';
import { formatBps, formatMetric, formatTimestamp, renderBadge, showToast } from './utils.js';

let activePollTimer = null;
let currentFilter = 'ALL';
let currentSearch = '';
let cachedSims = [];

export async function refreshSimulationsData(silent = false) {
    const tbody = document.getElementById("simulations-tbody");
    const refreshBtnIcon = document.getElementById("sim-refresh-icon");

    if (refreshBtnIcon) refreshBtnIcon.classList.add("spin");

    try {
        const sims = await api.getSimulations({ limit: 150 });
        cachedSims = sims;

        updateStatsCounters(sims);
        renderTableBody(sims);

        // Schedule next background poll only if there are running jobs and user is on simulations page
        if (activePollTimer) {
            clearTimeout(activePollTimer);
            activePollTimer = null;
        }

        const hasRunning = sims.some(s => s.status === 'RUNNING' || s.status === 'SUBMITTING');
        if (hasRunning) {
            activePollTimer = setTimeout(() => {
                const curPage = window.location.hash.replace('#', '') || 'dashboard';
                if (curPage === 'simulations') {
                    refreshSimulationsData(true);
                }
            }, 3000);
        }
    } catch (err) {
        if (!silent && tbody) {
            tbody.innerHTML = `<tr><td colspan="11" style="text-align: center; color: var(--status-danger); padding: 20px;">Failed to refresh simulations: ${err.message}</td></tr>`;
        }
    } finally {
        if (refreshBtnIcon) refreshBtnIcon.classList.remove("spin");
    }
}

function updateStatsCounters(sims) {
    const total = sims.length;
    const valid = sims.filter(s => s.has_valid_metrics || s.metrics_status === 'AVAILABLE').length;
    const running = sims.filter(s => s.status === 'RUNNING' || s.status === 'SUBMITTING').length;
    const failed = sims.filter(s => s.classification === 'TECHNICAL_FAILURE' || s.classification === 'REMOTE_FAILURE' || s.classification === 'AUTH_FAILURE' || s.classification === 'ALPHA_FAILURE' || s.classification === 'PORTFOLIO_EMPTY' || s.portfolio_status === 'EMPTY').length;

    const countAll = document.getElementById("sim-count-all");
    const countValid = document.getElementById("sim-count-valid");
    const countRunning = document.getElementById("sim-count-running");
    const countFailed = document.getElementById("sim-count-failed");

    if (countAll) countAll.textContent = total;
    if (countValid) countValid.textContent = valid;
    if (countRunning) countRunning.textContent = running;
    if (countFailed) countFailed.textContent = failed;

    // Update Telemetry Yield Bar widths & percentages
    const yieldRateEl = document.getElementById("sim-yield-rate");
    const barValid = document.getElementById("bar-segment-valid");
    const barRunning = document.getElementById("bar-segment-running");
    const barFailed = document.getElementById("bar-segment-failed");

    const validPct = total > 0 ? (valid / total * 100).toFixed(1) : '0.0';
    const runningPct = total > 0 ? (running / total * 100).toFixed(1) : '0.0';
    const failedPct = total > 0 ? (failed / total * 100).toFixed(1) : '0.0';

    if (yieldRateEl) yieldRateEl.textContent = `${validPct}% Success Yield`;
    if (barValid) {
        barValid.style.width = `${validPct}%`;
        barValid.title = `Valid Alphas: ${valid} (${validPct}%)`;
    }
    if (barRunning) {
        barRunning.style.width = `${runningPct}%`;
        barRunning.title = `In Progress: ${running} (${runningPct}%)`;
    }
    if (barFailed) {
        barFailed.style.width = `${failedPct}%`;
        barFailed.title = `Technical Failures: ${failed} (${failedPct}%)`;
    }
}

function renderTableBody(sims) {
    const tbody = document.getElementById("simulations-tbody");
    const emptyState = document.getElementById("simulations-empty-state");
    const tableContainer = document.getElementById("simulations-table-container");
    if (!tbody) return;

    let filtered = sims;

    if (currentFilter === 'VALID') {
        filtered = filtered.filter(s => s.has_valid_metrics || s.metrics_status === 'AVAILABLE');
    } else if (currentFilter === 'RUNNING') {
        filtered = filtered.filter(s => s.status === 'RUNNING' || s.status === 'SUBMITTING');
    } else if (currentFilter === 'FAILED') {
        filtered = filtered.filter(s => s.classification !== 'VALID_METRICS' && s.status !== 'RUNNING' && s.status !== 'SUBMITTING');
    }

    if (currentSearch.trim()) {
        const q = currentSearch.toLowerCase().trim();
        filtered = filtered.filter(s => 
            (s.expression && s.expression.toLowerCase().includes(q)) ||
            (s.id && s.id.toLowerCase().includes(q)) ||
            (s.brain_sim_id && s.brain_sim_id.toLowerCase().includes(q)) ||
            (s.family_code && s.family_code.toLowerCase().includes(q))
        );
    }

    if (filtered.length === 0) {
        if (tableContainer) tableContainer.style.display = "none";
        if (emptyState) {
            emptyState.style.display = "block";
            emptyState.innerHTML = `
                <div style="text-align: center; padding: 48px; color: var(--text-muted);">
                    <i data-lucide="inbox" style="width: 36px; height: 36px; margin-bottom: 10px; opacity: 0.6;"></i>
                    <h4 style="font-size: 15px; font-weight: 700; color: var(--text-main); margin-bottom: 6px;">
                        ${sims.length === 0 ? 'No Simulations Submitted Yet' : 'No Matching Simulations Found'}
                    </h4>
                    <p style="font-size: 13px; max-width: 420px; margin: 0 auto 16px auto;">
                        ${sims.length === 0 ? 'Generate candidates in Alpha Lab or synthesize hypothesis mutations to begin backtesting.' : 'Try adjusting your search query or filter criteria.'}
                    </p>
                    ${sims.length === 0 ? `
                        <button class="btn btn-primary btn-sm" onclick="window.verdeUI.navigateTo('alpha-lab')">
                            <i data-lucide="sparkles"></i> Open Alpha Lab
                        </button>
                    ` : ''}
                </div>
            `;
            if (window.lucide) window.lucide.createIcons();
        }
        return;
    }

    if (tableContainer) tableContainer.style.display = "block";
    if (emptyState) emptyState.style.display = "none";

    tbody.innerHTML = filtered.map(s => {
        const showDiag = s.classification !== "VALID_METRICS" && s.status !== "RUNNING" && s.status !== "SUBMITTING";
        const isRunning = s.status === "RUNNING" || s.status === "SUBMITTING";

        return `
            <tr>
                <td>
                    <div style="font-family: monospace; font-size: 12px; font-weight: 700;">
                        SIM-${s.id.substring(0, 8)}
                    </div>
                    ${s.brain_sim_id ? `<div style="font-size: 11px; color: var(--text-muted);"><code>${s.brain_sim_id}</code></div>` : ''}
                </td>
                <td>
                    <code class="code-expr" style="font-size: 12px; max-width: 300px; display: inline-block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        ${s.expression || 'N/A'}
                    </code>
                </td>
                <td><span class="badge badge-info">${s.family_code || 'GENERIC'}</span></td>
                <td>${renderBadge(s.remote_status || s.status)}</td>
                <td>${renderBadge(s.classification)}</td>
                <td>${renderBadge(s.portfolio_status)}</td>
                <td>${formatMetric(s.sharpe, 2)}</td>
                <td>${formatMetric(s.fitness, 2)}</td>
                <td>${formatMetric(s.turnover, 3)}</td>
                <td>${formatBps(s.margin_bps, 2)}</td>
                <td>
                    <div style="display: flex; gap: 6px; align-items: center;">
                        ${showDiag ? `
                            <button class="btn btn-outline btn-sm" onclick="window.verdeUI.openDiagnosticModal('${s.id}')" style="color: var(--status-warning); border-color: var(--status-warning);" title="View Telemetry Diagnostics">
                                <i data-lucide="alert-triangle" style="width: 12px; height: 12px;"></i> Diag
                            </button>
                        ` : ''}
                        ${isRunning ? `
                            <button class="btn btn-outline btn-sm" onclick="window.verdeUI.pollSimulation('${s.id}')" title="Force Re-Poll BRAIN">
                                <i data-lucide="refresh-cw" class="spin" style="width: 12px; height: 12px;"></i> Poll
                            </button>
                        ` : ''}
                        <button class="btn btn-outline btn-sm" onclick="window.verdeUI.openCandidateModal('${s.candidate_id}')" title="Inspect Candidate">
                            <i data-lucide="microscope" style="width: 12px; height: 12px;"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');

    if (window.lucide) window.lucide.createIcons();
}

export async function renderSimulations(container) {
    if (activePollTimer) {
        clearTimeout(activePollTimer);
        activePollTimer = null;
    }

    container.innerHTML = `
        <!-- Unified Quantitative Telemetry Ribbon -->
        <div class="telemetry-ribbon-container">
            <!-- Left Hero Pill -->
            <div class="telemetry-badge-hero" id="chip-filter-hero" title="View All Simulations">
                <div class="pulse-indicator">
                    <span class="pulse-dot"></span>
                    <span class="pulse-ring"></span>
                </div>
                <div class="telemetry-hero-details">
                    <span class="telemetry-label">Total Runs</span>
                    <span class="telemetry-value" id="sim-count-all">-</span>
                </div>
            </div>

            <!-- Center Visual Yield Distribution Meter -->
            <div class="telemetry-yield-wrapper">
                <div class="yield-bar-header">
                    <span class="yield-bar-title"><i data-lucide="bar-chart-2" style="width: 14px; height: 14px;"></i> Alpha Yield Distribution</span>
                    <span class="yield-bar-percentage" id="sim-yield-rate">0.0% Success Yield</span>
                </div>
                <div class="yield-progress-bar">
                    <div class="yield-segment segment-valid" id="bar-segment-valid" style="width: 0%;" title="Valid Alphas"></div>
                    <div class="yield-segment segment-running" id="bar-segment-running" style="width: 0%;" title="In Progress"></div>
                    <div class="yield-segment segment-failed" id="bar-segment-failed" style="width: 0%;" title="Technical Failures"></div>
                </div>
            </div>

            <!-- Right Interactive Metric Filter Chips -->
            <div class="telemetry-chips-group">
                <button class="telemetry-chip active" id="chip-filter-all">
                    <i data-lucide="layers" style="width: 13px; height: 13px;"></i>
                    <span class="chip-label">All Runs</span>
                </button>
                <button class="telemetry-chip chip-valid" id="chip-filter-valid">
                    <span class="chip-dot dot-valid"></span>
                    <i data-lucide="check-circle-2" style="width: 13px; height: 13px; color: #16a34a;"></i>
                    <span class="chip-label">Valid Alphas</span>
                    <span class="chip-count" id="sim-count-valid">-</span>
                </button>
                <button class="telemetry-chip chip-running" id="chip-filter-running">
                    <span class="chip-dot dot-running"></span>
                    <i data-lucide="loader" style="width: 13px; height: 13px; color: #ca8a04;"></i>
                    <span class="chip-label">In Progress</span>
                    <span class="chip-count" id="sim-count-running">-</span>
                </button>
                <button class="telemetry-chip chip-failed" id="chip-filter-failed">
                    <span class="chip-dot dot-failed"></span>
                    <i data-lucide="alert-octagon" style="width: 13px; height: 13px; color: #ef4444;"></i>
                    <span class="chip-label">Failures</span>
                    <span class="chip-count" id="sim-count-failed">-</span>
                </button>
            </div>
        </div>

        <!-- Main Card Container -->
        <div class="card">
            <!-- Header with Controls -->
            <div class="card-header" style="flex-wrap: wrap; gap: 14px; margin-bottom: 20px;">
                <div>
                    <h3 class="card-title">
                        <i data-lucide="play-circle" style="color: var(--verde-primary);"></i> WorldQuant BRAIN Simulation Monitor
                    </h3>
                    <span class="card-subtitle">
                        Real-time quantitative backtest telemetry isolating technical anomalies from alpha metrics
                    </span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <button class="btn btn-outline btn-sm" id="btn-manual-refresh" title="Refresh Telemetry">
                        <i data-lucide="refresh-cw" id="sim-refresh-icon"></i> Refresh
                    </button>
                    <button class="btn btn-primary btn-sm" onclick="window.verdeUI.navigateTo('alpha-lab')">
                        <i data-lucide="plus"></i> New Alpha Lab Run
                    </button>
                </div>
            </div>

            <!-- Filters & Search Toolbar -->
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; padding: 12px 16px; background: #f8fafc; border-radius: var(--radius-md); border: 1px solid var(--border-light);">
                <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                    <button class="btn btn-sm ${currentFilter === 'ALL' ? 'btn-primary' : 'btn-outline'}" id="filter-btn-all" style="font-size: 12px;">
                        All Runs
                    </button>
                    <button class="btn btn-sm ${currentFilter === 'VALID' ? 'btn-primary' : 'btn-outline'}" id="filter-btn-valid" style="font-size: 12px;">
                        <i data-lucide="check-circle" style="width: 12px; height: 12px;"></i> Valid Metrics
                    </button>
                    <button class="btn btn-sm ${currentFilter === 'RUNNING' ? 'btn-primary' : 'btn-outline'}" id="filter-btn-running" style="font-size: 12px;">
                        <i data-lucide="activity" style="width: 12px; height: 12px;"></i> In Progress
                    </button>
                    <button class="btn btn-sm ${currentFilter === 'FAILED' ? 'btn-primary' : 'btn-outline'}" id="filter-btn-failed" style="font-size: 12px;">
                        <i data-lucide="alert-triangle" style="width: 12px; height: 12px;"></i> Failures / Empty
                    </button>
                </div>
                <div style="min-width: 220px; flex: 1; max-width: 320px;">
                    <input type="text" id="sim-search-input" class="form-control" placeholder="Search formula, ID, family..." value="${currentSearch}" style="padding: 6px 12px; font-size: 12.5px;" />
                </div>
            </div>

            <!-- Table Container -->
            <div id="simulations-table-container" class="table-container">
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
                    <tbody id="simulations-tbody">
                        <tr>
                            <td colspan="11" style="text-align: center; padding: 40px; color: var(--text-muted);">
                                <i data-lucide="loader" class="spin" style="width: 24px; height: 24px; margin-bottom: 8px; color: var(--verde-primary);"></i>
                                <div>Loading simulation telemetry...</div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Empty State Fallback -->
            <div id="simulations-empty-state" style="display: none;"></div>
        </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    // Bind Filter Buttons & Telemetry Chips
    const setFilter = (filterVal) => {
        currentFilter = filterVal;
        ['all', 'valid', 'running', 'failed'].forEach(f => {
            const btn = document.getElementById(`filter-btn-${f}`);
            const chip = document.getElementById(`chip-filter-${f}`);
            const isMatch = f.toUpperCase() === filterVal;
            
            if (btn) {
                btn.className = `btn btn-sm ${isMatch ? 'btn-primary' : 'btn-outline'}`;
            }
            if (chip) {
                if (isMatch) {
                    chip.classList.add('active');
                } else {
                    chip.classList.remove('active');
                }
            }
        });
        renderTableBody(cachedSims);
    };

    ['all', 'valid', 'running', 'failed'].forEach(f => {
        const filterVal = f.toUpperCase();
        document.getElementById(`filter-btn-${f}`)?.addEventListener("click", () => setFilter(filterVal));
        document.getElementById(`chip-filter-${f}`)?.addEventListener("click", () => setFilter(filterVal));
    });
    document.getElementById("chip-filter-hero")?.addEventListener("click", () => setFilter("ALL"));

    // Bind Search Input
    document.getElementById("sim-search-input")?.addEventListener("input", (e) => {
        currentSearch = e.target.value;
        renderTableBody(cachedSims);
    });

    // Manual Refresh Button
    document.getElementById("btn-manual-refresh")?.addEventListener("click", () => {
        refreshSimulationsData(false);
    });

    // Initial Data Fetch
    await refreshSimulationsData(false);
}
